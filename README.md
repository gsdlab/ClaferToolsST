Clafer Tools
============

v0.5.4

Integration of the [Clafer compiler and instance generators](https://www.clafer.org) into [Sublime Text 4](https://www.sublimetext.com/).

Contributors
------------

* [Michał Antkiewicz](https://github.com/mantkiew), Main developer.

Features and Usage
------------------

In a Clafer model (`.cfr`):

* Syntax highlighting of keywords, operators, comments, strings and numbers, compiler directives
  (`//# OPTIONS` on the first line, `//# FRAGMENT`, `//# GRAPH`, `//# STATS`, `//# SUMMARY`),
  and embedded Alloy and JavaScript (`[alloy| … |]`, `[choco| … |]`).
* Compilation `ctrl+b` (`Tools > Build`): the compiler's errors are shown in the model, at their position,
  and its output in a panel. An error in a file that the model imports (`--import`, Clafer 0.5.4) is shown at the start
  of the model, with the file and the position in it, and in that file if it is open; double-click the error's underlined
  position in the panel, or press `F4`, to open the file at the error. The variant `Validate` (`ctrl+shift+b`) also validates the generated outputs
  with Alloy and chocosolver.
* Instance generation in a [Terminus](https://packagecontrol.io/packages/Terminus) tab:
  * Alloy-based instance generator (claferIG) `ctrl+i, g, a`
  * Choco-based instance generator (chocosolver) `ctrl+i, g, c`
* The Command Palette has the same commands under `Clafer:`.

Installation
------------

1. Install [Sublime Text 4](https://www.sublimetext.com/download).
2. In Sublime Text, install the packages `Clafer Tools` and `Terminus` with Package Control:
   `Tools > Command Palette > Package Control: Install Package`.
3. Download a [binary distribution of the Clafer tools](https://wiselab.uwaterloo.ca/clafer-tools-binary-distributions)
   and unpack it into a folder of your choice. The instance generators need Java 21 or later.
4. Either add that folder to `PATH`, or set `tools_path` to it in
   `Preferences > Package Settings > Clafer Tools > Settings`.

Settings
--------

* `tools_path`: the folder of the Clafer tools (`clafer`, `claferIG`, `chocosolver.jar`, `alloy6.2.0.jar`).
  Empty (the default): use the tools on `PATH`.
* `clafer_args`: the arguments of `clafer` for compilation; the model is added at the end.
  Default: `["-m", "alloy", "-m", "choco", "-m", "html", "--self-contained"]`.

Development
-----------

`syntax_test_clafer.cfr` tests the syntax: open it and run `Tools > Build With… > Syntax Tests`.
