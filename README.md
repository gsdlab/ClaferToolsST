Clafer Tools
=============

v0.3.7

Integration of [Clafer Compiler and Instance Generators](http://clafer.org) into [Sublime Text 2/3](http://www.sublimetext.com/).

Contributors
------------

* [Michał Antkiewicz](http://gsd.uwaterloo.ca/mantkiew), Main developer.

Features and Usage
------------------

* Syntax highlighting of keywords, operators, comments, and integer and string literals
* Compilation `<CTRL>+b`
* Instance generation using
   * Alloy-based instance generator with simple scope inference `<CTRL>+i, g, s`
   * Alloy-based instance generator with full scope inference `<CTRL>+i, g, f`
   * Choco-based instance generator with simple scope inference `<CTRL>+i, g, c`
   * Z3 SMT-based instance generator with simple scope inference `<CTRL>+i, g, m`

Installation
------------

1. Install [Sublime Text 3](http://www.sublimetext.com/3) or [Sublime Text 2](http://www.sublimetext.com/2)
2. In Sublime Text
   * Install [Package Control](https://sublime.wbond.net/installation)
   * Install packages `SublimeREPL`, `Clafer Tools` and (optionally) `SidebarEnhancements` 
      * `Preferences->Package Control->Install Package` 
      * type the name of the package
   * Open the `Packages` folder 
      * `Preferences->Browse Packages...`
      * copy the folder `SublimeREPL` from `Clafer Tools` to `Packages`
3. Download the latest binary distribution of Clafer Tools
   * [Clafer Tools](http://gsd.uwaterloo.ca/clafer-tools-binary-distributions)
   * Unzip the contents of the folder `clafer-tools-0.3.*` into `Packages/Clafer Tools`
      * Make sure the folder structure is NOT `Packages/Clafer Tools/clafer-tools-0.3.*`

### Known Limitations

* Works well only on Windows. 
* ClaferSMT in Clafer Tools 0.3.6.1 binary depends on the python package `bintrees`, to install execute `pip install bintrees` on Windows or `pip3 install bintrees` on Linux and Mac. 
* On Linux and Mac
   * the Python 3 executable is called `python3` and the best solution is to create a symlink called `python`  pointing to `/usr/bin/python3`.
   * it's also needed to add the current directory `.` to the `PATH`, so that the executables are found.

Planned Improvements
--------------------

* Code snippets for quantified expressions such as `[ all disj x1; x2 : X | ... ]`