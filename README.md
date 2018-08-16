# PyWebCopy &copy; 2.0.0

`Created By : Raja Tomar`
`License : MIT`

Mirrors Complete webpages with python.

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

## 1.1 Installation

`pywebcopy` is available on PyPi and is easily installable using `pip`

```Python
pip install pywebcopy
```

## 1.2 Basic Usages

### 1.2.1 Direct Function Methods
To mirror any single page, just type in python console

```Python
from pywebcopy.core import save_webpage


save_webpage(
    url='http://example-site.com/index.html',
    download_loc='path/to/downloads'
)
```

To mirror full website (This could overload the target server, So, be careful)

```Python
from pywebcopy.core import save_webpage


save_webpage(
    url='http://example-site.com/index.html',
    download_loc='path/to/downloads',
    copy_all=True
)
```

### 1.2.2 Object Creation Method

```Python
from pywebcopy.structures import WebPage

url = 'http://example-site.com/index.html'
download_loc = 'path/to/downloads/folder'

wp = WebPage(url, download_loc)

# if you want assets only
wp.save_assets_only()

# if you want html only
wp.save_html_only()

# if you want complete webpage
wp.save_complete()

# bonus : you can also use any beautiful_soup methods on it
links = wp.find_all('a', href=True)

```

that's it.

You will now have a folder at `download_loc` with all the webpage and its linked files ready to be used.

Just browse it as would on any browser!

## 1.3 Configuration

`pywebcopy` is highly configurable.

### 1.3.1 Direct Call Method

To change any configuration, just pass it to the `init` call.

Example:

```Python
from pywebcopy.core import save_webpage

save_webpage(

    url='http://some-site.com/', # required
    download_loc='path/to/downloads/', # required

    # config keys are case-insensitive
    any_config_key='new_value',
    another_config_key='another_new_value',

    ...

    # add many as you want :)
)
```

### 1.3.2 `core.setup_config` Method

You can manually configure every configuration by using a 
`core.setup_config` call.

```Python

import pywebcopy

url = 'http://example-site.com/index.html'
download_loc = 'path/to/downloads/'

pywebcopy.core.setup_config(url, download_loc)

# done!

>>> pywebcopy.config.config['url']
'http://example-site.com/index.html'

>>> pywebcopy.config.config['mirrors_dir']
'path/to/downloads'

>>> pywebcopy.config.config['project_name']
'example-site.com'


## You can also change any of these by just adding param to
## `setup_config` call

>>> pywebcopy.core.setup_config(url, 
        download_loc,project_name='Your-Project', ...)

## You can also change any config even after
## the `setup_config` call

pywebcopy.config.config['url'] = 'http://url-changed.com'
# rest of config remains unchanged

```

Done!

### 1.3.3 List of available `configurations`

below is the list of `config` keys with their `default` values :

``` Python
# writes the trace output and log file content to console directly
'DEBUG': False  

# make zip archive of the downloaded content
'MAKE_ARCHIVE': True

# delete the project folder after making zip archive of it
'CLEAN_UP': False

# which parser to use when parsing pages
# for speed choose 'html.parser' (will crack some webpages)
# for exact webpage copy choose 'html5lib' (a little slow)
# or you can leave it to default 'lxml' (balanced)
'PARSER' : 'lxml'

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
'MIRRORS_DIR': None

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
'USER_AGENT' : Mozilla/5.0 (compatible; WebCopyBot/X.X;)

# bypass the robots.txt restrictions
'BYPASS_ROBOTS' : False
```

told you there were plenty of `config` vars available!

## 1.4 Help

For any queries related to this project you can email me at
`rajatomar788@gmail.com`

You can help in many ways:

- reporting bugs
- sending me patches to fix or improve the code
- in generating the complete documentation of this project

Thanks!

## 1.5 Undocumented Features

I built many utils and classes in this project to ease 
the tasks I was trying to do.

But,
these task are also suitable for general purpose use.

So,
if you want, you can help in generating suitable `documentation` for these undocumented ones, then you can always email me.

## 1.6 Changelog

### [version 2.0.0]

- html-parser is now defaulted to 'lxml'. You can use any through new `config.config` key called `parser`
- fixed issue in `generators.extract_css_urls` which was caused by `str` and `bytes` difference in python3
- fixed minor issues while modules importing. (Thanks **Илья Игоревич**)
- added `errorhandling` to required functions


### [version 2.0(beta)]

- `init` function is replaced with `save_webpage`
- three new `config` automation functions are added -
  - `core.setup_config` (creates every ideal config just from url and download location)
  - `config.reset_config` (resets the configuration to default state)
  - `config.update_config` (manual-mode version of `core.setup_config`)  
- object `structures.WebPage` added
- merged `generators.generate_style_map` and `generators.generate_relative_paths` to a single function `generators.generate_style_map`
- rewrite of majority of functions
- new module `exceptions` added


### [version 1.10]

- `url` is checked and resolved of any redirection before starting any work functions.
- `init` vars : `mirrors_dir` and `clean_up` were fixed which cleaned the dir before the log was completely written.
- `init` call now takes `url` arg by default and could raise a error when not supplied
- professional looking log entries
- rewritten archiving system now uses `zipfile` and `exceptions` handling to prevent errors and eventual archive corruption

### [version 1.9]

- more redundant code
- modules are now separated based on type e.g. Core, Generators, Utils etc.
- new helper functions and class `structures.WebPage`
- Compatible with Python 2.6, 2.7, 3.6, 3.7
