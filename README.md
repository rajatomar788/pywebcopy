# PyWebCopy &copy;

`Created By : Raja Tomar`
`License : MIT`

Website mirroring and archiving tool written in Python
Archive any online website and its assets, css, js and
images for offilne reading, storage or whatever reasons.
It's easy with `pywebcopy`.

Why it's great? because it -

- respects `robots.txt`
- have a single-function basic usages
- lots of configuration for many custom needs
- many `utils` and `generator` functions to ease extraction of any part of website

Email me at `rajatomar788@gmail.com` of any query :)

## Installation

`pywebcopy` is available on PyPi and is easily installable using `pip`

```Python
pip install pywebcopy
```

## Basic Usages

To mirror any single page, just type in python console

```Python
from pywebcopy.core import init

init(url='http://example-site.com/index.html')
```

To mirror full website (This could overload the target server, So, be careful)

```Python
from pywebcopy.core import init

init(
    url='http://example-site.com/index.html',
    copy_all = True
    )
```

that's it.

You will now have a folder in C: drive
`C:\WebCopyProjects\example-site.com\example-site.com\`

Just browse it as would on any browser!

## Configuration

`pywebcopy` is highly configurable.

To change any configuration, just pass it to the `init` call.

Example:

```Python
from pywebcopy.core import init

init(

    url='http://some-site.com/', # required

    # config keys are case-insensitive
    any_config_key='new_value',
    another_config_key='another_new_value',

    ...

    # add many as you want :)
)
```

Done!

### List of available `configurations`

below is the list of `config` keys with their `default` values :

``` Python
# writes the log file content to console directly
'DEBUG': False  

# make zip archive of the downloaded content
'MAKE_ARCHIVE': True

# delete the project folder after making zip archive of it
'CLEAN_UP': False

# to download css file or not
'LOAD_CSS': True

# to download images or not
'LOAD_IMAGES': True

# to download js file or not
'LOAD_JAVASCRIPT': True

# to download every page available inside 
# url tree turn this True
# NOTE: This could overload the server and could 
# result in ip ban
'COPY_ALL': False

# to overwrite the existing files if found
'OVER_WRITE': False

# list of allowed file extensions
'ALLOWED_FILE_EXT': ['.html', '.css', '.json', '.js',
                     '.xml','.svg', '.gif', '.ico',
                      '.jpeg', '.jpg', '.png', '.ttf',
                      '.eot', '.otf', '.woff']

# file to write all valid links found on pages
'LINK_INDEX_FILE': None

# log file path
'LOG_FILE': None

# compress log by removing unnecessary info from log file
'LOG_FILE_COMPRESSION': False

# log buffering store log in ram until finished, then write to file
# Turning it on can reduce task completion time
'LOG_BUFFERING': True

# log buffer holder for performance speed up
# Can change this to your preferable cache provider :)
'LOG_BUFFER_ARRAY': list()

# name of the mirror project
'PROJECT_NAME': website-name.com

# url to download
'URL': None

# define the base directory to store all copied sites data
'MIRRORS_DIR': C:/WebCopyProjects/ + Project_Name

# all downloaded file location
# available after any project completion
'DOWNLOADED_FILES': list()


# DANGER ZONE
# CHANGE THESE ON YOUR RESPONSIBILITY
# NOTE: Do not change unless you know what you're doing

# pattern is used to check file name is supported by os
# FS, you can also change this to allow files of
# specific chars
'FILENAME_VALIDATION_PATTERN': re.compile(r'[*":<>\|\?]+')

# user agent to be shown on requests made to server
'USER_AGENT' : Mozilla/4.0 (compatible; WebCopyBot/X.X;
                +Non-Harmful-LightWeight)

# bypass the robots.txt restrictions
'BYPASS_ROBOTS' : False
```

told you there were plenty of `config` vars available!

## Help

For any queries related to this project you can email me at
`rajatomar788@gmail.com`

You can help in many ways:

- reporting bugs
- sending me patches to fix or improve the code
- in generating the complete documentation of this project

Thanks!

## Undocumented Features

I built many utils and classes in this project to ease 
the tasks I was trying to do.

But,
these task are also suitable for general purpose use.

So,
if you want, you can help in generating suitable `documentation` for these undocumented ones, then you can always email me.

## Changelog

### [version 1.9]

- more redundant code
- modules are now separated based on type e.g. Core, Generators, Utils etc.
- new helper functions and class `structures.WebPage`
- Compatible with Python 2.6, 2.7, 3.6, 3.7

### [version 1.10]

- `url` is checked and resolved of any redirection before starting any work functions.
- `init` vars : `mirrors_dir` and `clean_up` were fixed which cleaned the dir before the log was completely written.
- `init` call now takes `url` arg by default and could raise a error when not supplied
- professional looking log entries
- rewritten archiving system now uses `zipfile` and `exceptions` handling to prevent errors and eventual archive corruption
