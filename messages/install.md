Thank you for installing Clafer Tools for Sublime Text 2/3.

To finish the installation

1. Open Sublime's `Packages` folder
   * `Preferences->Browse Packages...`
   * copy the folder `SublimeREPL` from `Clafer Tools` to `Packages`
2. Download the latest binary distribution of Clafer Tools
   * [Clafer Tools](http://gsd.uwaterloo.ca/clafer-tools-binary-distributions)
   * Unzip the contents of the folder `clafer-tools-0.4.4` into `Packages/Clafer-Bin`
      * Make sure the folder structure is NOT `Packages/Clafer-Bin/clafer-tools-0.4.4`, that is, the contents of the folder `clafer-tools-0.4.4` are directly inside `Clafer-Bin`
   * add `Clafer-Bin` to the variable `PATH`.
4. On Windows only
   * Alloy-based instance generator only works with 32bit Java on Windows and if you only have 64bit Java installation, you will see an error: `Exception in thread "main" java.lang.UnsatisfiedLinkError: no minisatproverx1 in java.library.path`.

### Known Limitations and Workarounds

* On Windows - Setting the PATH to 32bit Java installation
   * install [32bit JDK](http://www.oracle.com/technetwork/java/javase/downloads/jdk8-downloads-2133151.html) but do not modify the PATH to point to it (there's no 32bit JRE anymore)
   * in Sublime Text
      * `Preferences->Package Settings->SublimeREPL->Settings - Default`
      * set `default_extended_env` as `"default_extend_env": {"PATH": "C:/Program Files (x86)/Java/jdk1.8.0_102/bin;{PATH}"},`

* ClaferSMT in Clafer Tools 0.3.6.1 binary depends on the python package `bintrees`, to install execute `pip install bintrees` on Windows or `pip3 install bintrees` on Linux and Mac.

* On Linux and Mac
   * the Python 3 executable is called `python3` and the best solution is to create a symlink called `python`  pointing to `/usr/bin/python3`
      * in `Packages/Clafer Tools` execute `ln -s /usr/bin/python3 python`.
   * it's also needed to add the current directory `.` to the `PATH`, so that the executables are found. Add the following line at the end of your `.profile` or `.bashrc`
      * `PATH=".:$PATH"`
   * for python to be able to find the `Z3` library, add the following line to your `.profile` or `.bashrc`
      * on Linux, `export LD_LIBRARY_PATH="~/.config/sublime-text-3/Packages/Clafer-Bin:$LD_LIBRARY_PATH"`
      * on Mac, `export DYLD_LIBRARY_PATH="~/.config/sublime-text-3/Packages/Clafer-Bin:$DYLD_LIBRARY_PATH"`

* On MacOS Yosemite, the preferred way of setting the variable `PATH` is by editing `/etc/paths`. However, despite that, Sublime Text 2/3 will not see the specified values because it is a GUI application and it will only see `/usr/bin:/bin:/usr/sbin:/sbin:/`. To check the value of `PATH` visible to Sublime
   1. open console `View->Show Console`
   2. execute `import os; print (os.environ['PATH'])`
   3. if you see `/usr/bin:/bin:/usr/sbin:/sbin:/`, you are affected by the Yosemite `PATH` bug and ClaferChocoIG will be unable to comple the model for you because it calls the clafer executable.
   4. the workaround is to:
      * create a symlink `sudo ln -s ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Clafer-Bin/clafer /usr/bin/clafer` so that `clafer` executable will be visible on the default `PATH`.
   5. to conveniently use ClaferChocoIG, move the script `claferchocoig.sh` (included in Mac binary distro) to `/usr/bin` by executing `sudo mv ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Clafer-Bin/claferchocoig.sh /usr/bin`.
