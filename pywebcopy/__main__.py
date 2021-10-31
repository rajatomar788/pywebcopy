# Copyright 2020; Raja Tomar
# See license for more details
import os
import sys
import optparse
import six

from pywebcopy.__version__ import __title__
from pywebcopy.__version__ import __version__
from pywebcopy.__version__ import __description__
from pywebcopy import save_webpage
from pywebcopy import save_website


parser = optparse.OptionParser(
    usage='%prog [-p|--page|-s|--site|-t|--tests] '
          '[--url=URL [,--location=LOCATION [,--name=NAME '
          '[,--pop [,--bypass_robots [,--quite [,--delay=DELAY]]]]]]] ',
    version=__version__,
    prog=__title__,
    description=__description__
)

#: Multiple saving modes.
options = optparse.OptionGroup(parser, 'CLI Actions List', 'Primary actions available through cli.')
options.add_option('-p', '--page', action='store_true', help='Quickly saves a single page.')
options.add_option('-s', '--site', action='store_true', help='Saves the complete site.')
options.add_option('-t', '--tests', action='store_true', help='Runs tests for this library.')

parser.add_option_group(options)

#: Required params
parser.add_option('--url', type='string', help='url of the entry point to be retrieved.')
parser.add_option('--location', type='string', help='Location where files are to be stored.')

#: Optional params
parser.add_option('-n', '--name', default=None, type='string', help='Project name of this run.')
parser.add_option('-d', '--delay', type='float', help="Delay between consecutive requests to the server.")

#: Optional flags
parser.add_option('--bypass_robots', default=True, action='store_true', help='Bypass the robots.txt restrictions.')
parser.add_option('--threaded', default=False, action='store_true', help='Use threads for faster downloading.')
parser.add_option('-q', '--quite', default=False, action='store_true', help='Suppress the logging from this library.')
parser.add_option('--pop', default=False, action='store_true',
                  help='open the html page in default browser window after finishing the task.')

args, remainder = parser.parse_args()

# type checks
if bool(args.page) or bool(args.site):
    if not args.url or not isinstance(args.url, six.string_types):
        parser.error("--url option requires 1 string type argument")
    if args.location and not isinstance(args.location, six.string_types):
        parser.error("--location option requires 1 string type argument")
    if args.name and not isinstance(args.name, six.string_types):
        parser.error("--name option requires 1 string type argument")

if args.page:
    save_webpage(
        url=args.url,
        project_folder=args.location,
        bypass_robots=args.bypass_robots,
        open_in_browser=args.pop,
        debug=not args.quite,
        delay=args.delay,
        threaded=args.threaded,
    )
elif args.site:
    save_website(
        url=args.url,
        project_folder=args.location,
        bypass_robots=args.bypass_robots,
        open_in_browser=args.pop,
        debug=not args.quite,
        delay=args.delay,
        threaded=args.threaded,
    )
elif args.tests:
    os.system('%s -m unittest discover -s pywebcopy/tests' % sys.executable)
else:
    parser.print_help()
    sys.exit(1)
