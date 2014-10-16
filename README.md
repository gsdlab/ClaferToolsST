clafer-tools-portable
=====================

v0.3.7

Integration of [Clafer Tools](http://clafer.org) into [Sublime Text 3](http://www.sublimetext.com/).

Contributors
------------

* [Michał Antkiewicz](http://gsd.uwaterloo.ca/mantkiew), Main developer.

Features and Usage
------------------

* syntax highlighting
* compilation `<CTRL>+B`
* instance generation using
   * Alloy-based instance generator with simple scope inference `<CTRL>+i, g, s`
   * Alloy-based instance generator with full scope inference `<CTRL>+i, g, f`
   * Choco-based instance generator with simple scope inference `<CTRL>+i, g, c`
   * Z3 SMT-based instance generator with simple scope inference `<CTRL>+i, g, m`

Installation
------------

0. Install [Sublime Text 3](http://www.sublimetext.com/3)
1. In Sublime Text 3
   * Install [Package Control](https://sublime.wbond.net/installation)
   * Install packages SublimeREPL and SidebarExtensions (optionally)
      * `Preferences->Package Control->Install Package` 
      * type the name of the package
   * Open the `Packages` folder 
      * `Preferences->Browse Packages...`
2. Copy the folders `Clafer` and `SublimeREPL` from this project into your Sublime's `Packages` folder
3. Download the latest binary distribution of Clafer Tools
   * [Clafer Tools](http://gsd.uwaterloo.ca/clafer-tools-binary-distributions)
   * unzip the contents into `Packages/Clafer` 