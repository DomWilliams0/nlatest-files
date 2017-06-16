nlatest-files
=======================

Easy symlinks to the n latest files in a directory.

This is an tool that maintains symlinks to the n most recently modified
files in a given directory.

----

Installation
-------------
.. code-block:: 

    pip install nlatest-files

Usage
------
.. code-block:: 

    usage: nlf [-h] [-c FILE] [--save] -d DIR [-n COUNT] [-u] [-s DIR] [-f FORMAT]
               [-q]

    Args that start with '--' (eg. --save) can also be set in a config file
    (/home/user/.config/nlatest-files.conf or specified via -c). Config file syntax
    allows: key=value, flag=true, stuff=[a,b,c] (for details, see syntax at
    https://goo.gl/R74nmi). If an arg is specified in more than one place, then
    commandline values override config file values which override defaults.

    optional arguments:
      -h, --help            show this help message and exit
      -c FILE, --config FILE
                            config file location, defaults to
                            $XDG_CONFIG_HOME/nlatest-files.conf
      --save                if specified, saves the current configuration to the
                            config file
      -d DIR, --dir DIR     the source directory
      -n COUNT, --count COUNT
                            the latest n files to list, defaults to 1
      -u, --update-symlinks
                            create symlinks to the latest n files
      -s DIR, --symlink-dir DIR
                            the directory to create symlinks in, defaults to the
                            source directory
      -f FORMAT, --symlink-format FORMAT
                            the format string for symlinks, where {n} is the order
                            index, defaults to 'latest-{n}'. {n} must be included,
                            unless n = 1
      -q, --quiet           if specified, no status messages will be printed to
                            stderr

Examples
--------
.. code-block:: 

    nlf -d ~/invoices -n 5
        Prints the latest 5 files in ~/invoices

    nlf -d ~/invoices -n 5 --save
        Saves the given parameters to the default config file

    nlf -d ~/invoices -n 5 -c ~/dotfiles/myconfig.conf --save
        Saves the given parameters to the specified config file

    nlf
        Prints the latest 5 again, using from the config file

    nlf -u -s $HOME/screenshots -f "screeny-{n}" -n 3
        Creates symlinks to the top 3 latest screenshots in ~/screenshots

    scrot -e 'mv -u $f ~/screenshots/ && nlf -u -d ~/screenshots -n 1 -f "latest"'
        Takes a screenshot with scrot, moves it to ~/screenshots, then
        adds a `symlink ~/screenshots/latest` pointing to it


Future Plans
-------------
- [ ] file extension specifier
- [ ] multiple source directories
- [ ] recursive search

