Clafer Tools for Sublime Text 4
===============================

Thank you for installing Clafer Tools.

To finish the installation:

1. Download a binary distribution of the Clafer tools from
   https://wiselab.uwaterloo.ca/clafer-tools-binary-distributions
   and unpack it into a folder of your choice. The instance generators need Java 21 or later.
2. Either add that folder to `PATH`, or set `tools_path` to it in
   `Preferences > Package Settings > Clafer Tools > Settings`.
3. Install the package `Terminus` with Package Control, to run the instance generators.

Usage, in a Clafer model (`.cfr`):

* `Tools > Build` (`ctrl+b`) compiles the model and shows the compiler's errors in it;
  the variant `Validate` (`ctrl+shift+b`) also validates the generated outputs.
* `ctrl+i, g, a` runs the Alloy-based instance generator (claferIG),
  `ctrl+i, g, c` the Choco-based one (chocosolver), in a Terminus tab.
* The Command Palette has the same commands under `Clafer:`.
