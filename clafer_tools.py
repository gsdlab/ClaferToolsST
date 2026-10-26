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

# "Compile error at model.cfr:3:5..." or "Parse failed at model.cfr:3:5...", followed by the
# message; the file is the one in which the error is, a path relative to the model's folder or a
# URL. Before Clafer 0.5.4, "at line 3 column 5..." in the compiled file. A ClaferErr without a
# position prints "Error...".
ERROR = re.compile(r"^(?:Compile error|Parse failed) at (?:(.+):(\d+):(\d+)|line (\d+) column (\d+))\.\.\.$|^Error\.\.\.$", re.M)
# The errors with a file, for navigating from the output panel.
RESULT_FILE = r"^(?:Compile error|Parse failed) at (.+):(\d+):(\d+)\.\.\.$"
LINKS = "clafer_links"

# The views with the errors of each model by file name, to clear them on the next build.
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
    """The errors in clafer's output as (file, line, column, message): the file in which
    the error is (None for the compiled file), lines and columns from 1; line 0 if the
    error has no position."""
    errors = []
    matches = list(ERROR.finditer(output))
    for match, following in zip(matches, matches[1:] + [None]):
        end = following.start() if following else len(output)
        message = output[match.end():end].strip()
        if match.group(1):
            errors.append((match.group(1), int(match.group(2)), int(match.group(3)), message))
        elif match.group(4):
            errors.append((None, int(match.group(4)), int(match.group(5)), message))
        else:
            errors.append((None, 0, 0, message))
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


def show_errors(window, view, errors):
    """Shows the errors of the model in the view in the files in which they are: the model,
    or a file it imports if the file is open. An error in another file is also shown at the
    start of the model, where the imports are, with the file and the position in it."""
    model = os.path.normpath(view.file_name())
    by_view = {view.id(): (view, [])}
    for file, line, column, message in errors:
        path = model
        if file is not None:
            path = None if re.match(r"https?://", file) else os.path.normpath(os.path.join(os.path.dirname(model), file))
        if path == model:
            by_view[view.id()][1].append((line, column, message))
            continue
        target = window.find_open_file(path) if path else None
        if target is not None:
            by_view.setdefault(target.id(), (target, []))[1].append((line, column, message))
        by_view[view.id()][1].append((0, 0, "{}:{}:{}: {}".format(file, line, column, message)))
    for target, target_errors in by_view.values():
        regions, annotations = [], []
        for line, column, message in target_errors:
            point = text_point(target, line, column)
            word = target.word(point)
            regions.append(word if word.contains(point) and not word.empty() else sublime.Region(point, point))
            annotations.append(html.escape(message).replace("\n", "<br>"))
        target.add_regions(
            REGIONS, regions, scope="region.redish", icon="circle",
            flags=sublime.DRAW_SQUIGGLY_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE,
            annotations=annotations, annotation_color="#e06c75")
    _error_views[view.file_name()] = list(by_view)


def underline_links(panel):
    """Underlines the positions of the errors in the output panel (file:line:column), which
    open the file at the error with a double-click or F4."""
    text = panel.substr(sublime.Region(0, panel.size()))
    links = [sublime.Region(match.start(1), match.end(3)) for match in re.finditer(RESULT_FILE, text, re.M)]
    panel.add_regions(LINKS, links, scope="markup.underline.link",
                      flags=sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE | sublime.DRAW_SOLID_UNDERLINE)


def clear_errors(file_name):
    for view_id in _error_views.pop(file_name, []):
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
        panel.settings().set("result_file_regex", RESULT_FILE)
        panel.settings().set("result_base_dir", os.path.dirname(file_name))
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
            underline_links(panel)
            if errors and view.is_valid():
                show_errors(self.window, view, errors)
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
