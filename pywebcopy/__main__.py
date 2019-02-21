# encoding: utf8
"""
pywebcopy.__main__
~~~~~~~~~~~~~~~~~~

Command line usage provider for pywebcopy.

"""


from __future__ import print_function

import os
import sys
import textwrap

from pywebcopy import save_website, save_webpage, config


# Defaultly no following robots.txt
config['bypass_robots'] = True


USAGE = textwrap.dedent("""\
        Usage:
            pywebcopy [option] value [option2] value2 ...
        Options:            
            -t                                                  # runs all available tests
            -p  http://example.com/ -d /downloads/              # Save this webPage at /downloads/ folder
            -c  http://example.com/ -d /downloads/              # Save this webSite at /downloads/ folder      
        """)


def print_usage():
    print(USAGE)


args = sys.argv[1:]

if not args or args[0] not in ('-p', '-c', '-t'):
    print_usage()
    sys.exit(1)

if args[0] == '-t':
    os.system('{} -m unittest pywebcopy.tests'.format(sys.executable))

if args[0] == '-p':
    if len(args) < 2:
        print_usage()
        sys.exit(1)

    if len(args) == 2:
        print("Saving {!r} in {!r}".format(args[1], os.getcwd()))
        save_webpage(args[1], os.getcwd())

    elif len(args) == 4 and args[2] == '-d':
        print("Saving {!r} in {!r}".format(args[1], args[3]))
        save_webpage(args[1], args[3])

    else:
        print_usage()
        sys.exit(1)

elif args[0] == '-c':
    if len(args) < 2:
        print_usage()
        sys.exit(1)

    if len(args) == 2:
        print("Saving {!r} in {!r}".format(args[1], os.getcwd()))
        save_website(args[1], os.getcwd())

    elif len(args) == 4 and args[2] == '-d':
        print("Saving {!r} in {!r}".format(args[1], args[3]))
        save_website(args[1], args[3])

    else:
        print_usage()
        sys.exit(1)
