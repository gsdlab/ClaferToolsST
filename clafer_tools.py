"""Clafer Tools for Sublime Text 4: compiles Clafer models, shows the compiler's
errors in the model, and runs the instance generators in a Terminus tab."""

import html
import os
import re
import shutil
import subprocess
import threading

import sublime
import sublime_plugin

SETTINGS = "Clafer Tools.sublime-settings"
PANEL = "clafer"
REGIONS = "clafer_errors"

# "Compile error at line 3 column 5..." or "Parse failed at line 3 column 5...",
# followed by the message; a ClaferErr without a position prints "Error...".
ERROR = re.compile(r"^(?:Compile error|Parse failed) at line (\d+) column (\d+)\.\.\.$|^Error\.\.\.$", re.M)

# The view of each model by file name, to clear its errors on the next build.
_error_views = {}


def settings():
    return sublime.load_settings(SETTINGS)


def tools_dir():
    """The folder with the Clafer tools: the setting, or the folder of clafer on PATH."""
    configured = os.path.expanduser(settings().get("tools_path") or "")
    if configured:
        return configured
    found = shutil.which("clafer")
    return os.path.dirname(os.path.realpath(found)) if found else ""


def tools_env():
    """The environment for the tools: the configured folder first on PATH, since
    chocosolver runs clafer itself."""
    env = os.environ.copy()
    configured = os.path.expanduser(settings().get("tools_path") or "")
    if configured:
        env["PATH"] = configured + os.pathsep + env.get("PATH", "")
    return env


def tool(name):
    """The executable of a tool, in the configured folder or on PATH."""
    configured = os.path.expanduser(settings().get("tools_path") or "")
    if configured:
        for candidate in (name, name + ".exe"):
            path = os.path.join(configured, candidate)
            if os.path.isfile(path):
                return path
    return shutil.which(name, path=tools_env()["PATH"])


def is_clafer(view):
    return view is not None and view.file_name() is not None and view.match_selector(0, "source.clafer")


def parse_errors(output):
    """The errors in clafer's output as (line, column, message), from 1; line 0 if
    the error has no position."""
    errors = []
    matches = list(ERROR.finditer(output))
    for match, following in zip(matches, matches[1:] + [None]):
        end = following.start() if following else len(output)
        message = output[match.end():end].strip()
        if match.group(1):
            errors.append((int(match.group(1)), int(match.group(2)), message))
        else:
            errors.append((0, 0, message))
    return errors


def text_point(view, line, column):
    """The point of clafer's line and column: the compiler counts a tab as advancing
    to the next multiple of 8, plus 1. A position past the end of the line (the
    compiler's virtual closing brace) is the end of the line."""
    if line < 1 or line > view.rowcol(view.size())[0] + 1:
        return 0
    start = view.text_point(line - 1, 0)
    text = view.substr(view.line(start))
    visual = 1
    for offset, char in enumerate(text):
        if visual >= column:
            return start + offset
        visual = (visual + 7) // 8 * 8 + 1 if char == "\t" else visual + 1
    return start + len(text)


def show_errors(view, errors):
    regions, annotations = [], []
    for line, column, message in errors:
        point = text_point(view, line, column)
        word = view.word(point)
        regions.append(word if word.contains(point) and not word.empty() else sublime.Region(point, point))
        annotations.append(html.escape(message).replace("\n", "<br>"))
    view.add_regions(
        REGIONS, regions, scope="region.redish", icon="circle",
        flags=sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE,
        annotations=annotations, annotation_color="#e06c75")
    _error_views[view.file_name()] = view.id()


def clear_errors(file_name):
    view_id = _error_views.pop(file_name, None)
    if view_id is not None:
        sublime.View(view_id).erase_regions(REGIONS)


class ClaferBuildCommand(sublime_plugin.WindowCommand):
    """The target of Clafer.sublime-build: compiles the model in the active view
    and shows the errors in it."""

    process = None

    def run(self, validate=False, kill=False):
        if kill:
            if self.process:
                self.process.terminate()
            return
        view = self.window.active_view()
        if not is_clafer(view):
            sublime.status_message("Clafer: not a Clafer model")
            return
        clafer = tool("clafer")
        if not clafer:
            sublime.error_message("Clafer Tools: clafer was not found.\n\nAdd the folder of the "
                                  "Clafer tools to PATH or set tools_path in the package settings.")
            return
        file_name = view.file_name()
        cmd = [clafer] + settings().get("clafer_args", []) + [os.path.basename(file_name)]
        if validate:
            cmd[1:1] = ["--validate", "--tooldir=" + tools_dir()]
        clear_errors(file_name)
        panel = self.window.create_output_panel(PANEL)
        panel.run_command("append", {"characters": " ".join(cmd) + "\n"})
        self.window.run_command("show_panel", {"panel": "output." + PANEL})
        threading.Thread(target=self.compile, args=(cmd, file_name, view, panel), daemon=True).start()

    def compile(self, cmd, file_name, view, panel):
        try:
            self.process = subprocess.Popen(
                cmd, cwd=os.path.dirname(file_name), env=tools_env(),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = self.process.communicate()[0].decode("utf-8", "replace").replace("\r\n", "\n")
            code = self.process.returncode
        except OSError as error:
            output, code = str(error) + "\n", -1
        finally:
            self.process = None
        errors = parse_errors(output) if code != 0 else []

        def finish():
            panel.run_command("append", {"characters": output + "\n[exit code {}]\n".format(code)})
            if errors and view.is_valid():
                show_errors(view, errors)
            sublime.status_message("Clafer: {} error(s)".format(len(errors)) if code else "Clafer: compiled")
        sublime.set_timeout(finish)


class ClaferInstancesCommand(sublime_plugin.WindowCommand):
    """Runs an instance generator for the model in the active view in a Terminus tab:
    claferIG (Alloy) or chocosolver's REPL (Choco)."""

    def run(self, backend="choco"):
        view = self.window.active_view()
        if not is_clafer(view):
            return
        if view.is_dirty():
            view.run_command("save")
        file_name = view.file_name()
        if backend == "alloy":
            claferIG = tool("claferIG")
            if not claferIG:
                return self.not_found("claferIG")
            cmd = [claferIG, os.path.basename(file_name)]
        else:
            jar = os.path.join(tools_dir(), "chocosolver.jar")
            if not os.path.isfile(jar):
                return self.not_found("chocosolver.jar")
            cmd = ["java", "-jar", jar, "--repl", "--prettify", "--file", os.path.basename(file_name)]
        if not sublime.find_resources("Terminus.sublime-settings"):
            sublime.error_message("Clafer Tools: the instance generators run in a Terminus tab.\n\n"
                                  "Install the package Terminus with Package Control.")
            return
        self.window.run_command("terminus_open", {
            "cmd": cmd,
            "cwd": os.path.dirname(file_name),
            "env": {"PATH": tools_env()["PATH"]},
            "title": "{} ({})".format(os.path.basename(file_name), "Alloy" if backend == "alloy" else "Choco"),
            "auto_close": False,
        })

    def is_enabled(self, backend="choco"):
        return is_clafer(self.window.active_view())

    @staticmethod
    def not_found(name):
        sublime.error_message("Clafer Tools: {} was not found.\n\nAdd the folder of the Clafer tools "
                              "to PATH or set tools_path in the package settings.".format(name))
