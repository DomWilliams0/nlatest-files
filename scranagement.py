#!/usr/bin/env python3

import os
import glob
from collections import namedtuple

Config = namedtuple('Config', ['directory', 'latest_n'])


def get_n_latest(directory, n):
    # TODO check for missing directory
    files = [f for f in glob.glob("%s/*" % directory) if os.path.isfile(f)]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:n]


def main(conf):
    x = get_n_latest(conf.directory, conf.latest_n)
    print(x)


def _expand_path(path):
    return os.path.expanduser(os.path.expandvars(path))


def parse_args():
    # TODO parse from args
    directory = "$HOME/screenshots"
    n = 3
    return (True, Config(directory=_expand_path(directory), latest_n=n))


def show_usage():
    print("Usage: X")  # TODO


if __name__ == "__main__":
    (success, conf) = parse_args()
    if not success:
        show_usage()
        sys.exit(1)

    main(conf)
