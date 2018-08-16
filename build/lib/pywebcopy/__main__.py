# -*- coding: utf-8 -*-

"""
aerwebcopy.__main__

Command-Line operating for aerwebcoopy.
"""


import sys
import os
import core


# if argument is passed e.g. 'run'
if len(sys.argv) > 1:

    # get the required config values from '$ SET arg=value' types
    url = os.environ.get('URL')
    download_loc = os.environ.get('DOWNLOAD_LOC')

    # if any one is missing
    if url and download_loc:
        
        # if argument is 'run'
        if sys.argv[1] and sys.argv[1].lower() == 'run':
            # run the actual function
            core.save_webpage(url, download_loc)
        else:
            print('\nERROR : command %r is not valid!' % sys.argv[1])

    else:
        print('''
ERROR : Required config values are not declared : ('URL', 'DOWNLOAD_LOC')

USAGE : 
    On linux e.g. bash/shell:
        $ export URL = 'value'
        $ export DOWNLOAD_LOC = 'another_value'
        $ python -m pywebcopy run [options]

    On windows e.g. cmd:
        c:/windows/system32> SET URL = 'value'
        c:/windows/system32> SET DOWNLOAD_LOC = 'another_value'
        c:/windows/system32> SET python -m pywebcopy run [options] \
''')
        sys.exit(1)

else: pass