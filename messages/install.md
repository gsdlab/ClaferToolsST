Thank you for installing Clafer Tools for Sublime Text.

To finish the installation 

1. Open Sublime's `Packages` folder 
   * `Preferences->Browse Packages...`
   * copy the folder `SublimeREPL` from `Clafer Tools` to `Packages`
2. Download the latest binary distribution of Clafer Tools from
   * [Clafer Tools Binary Distributions](http://gsd.uwaterloo.ca/clafer-tools-binary-distributions)
3. Unzip the contents of the folder `clafer-tools-0.3.6.1` into `Packages/Clafer Tools`
   * Make sure the folder structure is NOT `Packages/Clafer Tools/clafer-tools-0.3.6.1`

4. ClaferSMT in Clafer Tools 0.3.6.1 binary depends on the python package `bintrees`, to install execute `pip install bintrees` on Windows or `pip3 install bintrees` on Linux and Mac. 

5. On Linux and Mac
   * the Python 3 executable is called `python3` and the best solution is to create a symlink called `python`  pointing to `/usr/bin/python3`
      * in `Packages/Clafer Tools` execute `ln -s /usr/bin/python3 python`.
   * it's also needed to add the current directory `.` to the `PATH`, so that the executables are found. Add the following line at the end of your `.profile` or `.bashrc`
      * `PATH=".:$PATH"`
   * for python to be able to find the `Z3` library, add the following line to your `.profile` or `.bashrc`
      * `export LD_LIBRARY_PATH="~/.config/sublime-text-3/Packages/Clafer Tools:$LD_LIBRARY_PATH"` 

