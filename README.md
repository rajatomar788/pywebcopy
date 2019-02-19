# PyWebCopy &copy; 5

`Created By : Raja Tomar`
`License : MIT`
`Email: rajatomar788@gmail.com`

Web Scraping and Saving Complete webpages and websites with python.

Web scraping and archiving tool written in Python
Archive any online website and its assets, css, js and
images for offilne reading, storage or whatever reasons.
It's easy with `pywebcopy`.

Why it's great? because it -

- respects `robots.txt`
- have a single-function basic usages
- lots of configuration for many custom needs
- provides several scraping packages in one Objects (thanks to their original owners)
  - beautifulsoup4
  - lxml
  - requests
  - requests_html
  - pyquery

Email me at `rajatomar788@gmail.com` of any query :)

## 1.1 Installation

`pywebcopy` is available on PyPi and is easily installable using `pip`

```Python
pip install pywebcopy
```

You are ready to go. Read the tutorials below to get started.

## First steps

You should always check if the pywebcopy is installed successfully.

```python
>>> import pywebcopy
>>> pywebcopy.__version___
5.x
```

Your version may be different, now you can continue the tutorial.

## 1.2 Basic Usages

To save any single page, just type in python console

```Python
from pywebcopy import save_webpage


save_webpage(
    url='http://example-site.com/index.html',
    project_folder='path/to/downloads'
)
```

To save full website (This could overload the target server, So, be careful)

```Python
from pywebcopy import save_website

save_website(
    url='http://example-site.com/index.html',
    project_folder='path/to/downloads',
)
```

### 1.2.1 Running Tests
Running tests is simple and doesn't require any external library. 
Just run this command from root directory of pywebcopy package


```shell
$ python -m unittest pywebcopy.tests
```

### 1.2.2 Webpage() object

```Python
from pywebcopy import WebPage

url = 'http://example-site.com/index.html' or None
project_loc = 'path/to/downloads/folder'

wp = WebPage(url,
project_folder
default_encoding=None,
HTML=None,
**configKwargs
)

# You can choose to load the page explicitly using 
# `requests` module
wp.get(url, **requestsKwargs)

# if you want assets only
wp.save_assets()

# if you want html only
wp.save_html()

# if you want complete webpage
wp.save_complete()
```

#### BeautifulSoup methods are supported

you can also use any beautiful_soup methods on it

```python
>>> links = wp.bs4.find_all('a')

['//docs.python.org/3/tutorial/', '/about/apps/', 'https://github.com/python/pythondotorg/issues', '/accounts/login/', '/download/other/']

```

### LXML is completely supported

You can use any lxml methods on it. Read more about lxml at `http://lxml.de/`

```python
>>> wp.lxml.xpath('//a', ..)
[<Element 'a'>,<Element 'a'>]

```

### PyQuery is Fully supported

You can use PyQuery methods on it .Read more about pyquery at `https://pythonhosted.org/pyquery/`

```python
>>> wp.pq.select(selector, ..)
...
```

### XPath is also supported

xpath is also natively supported which retures a :class: `requests_html.Element` See more at `https://html.python-requests.org`

```python

>>> wp.xpath('a')
[<Element 'a' class='btn' href='https://help.github.com/articles/supported-browsers'>]
```

### You can also select only elements containing certain text

```python
>>> wp.find('a', containing='kenneth')
[<Element 'a' href='http://kennethreitz.com/pages/open-projects.html'>, <Element 'a'
```

## Tutorials: sample use-cases with pywebcopy

## Common Settings and Errors

### `pywebcopy.exceptions.AccessError`

If you are getting `pywebcopy.exceptions.AccessError` Exception.
then check if website allows scraping of its content.

```python
>>> import pywebcopy
>>> pywebcopy.config['bypass_robots'] = True

# rest of your code follows..
```

### Overwrite existing files when copying

If you want to overwrite existing files in the directory then
use the over_write config key.

```python
>>> import pywebcopy
>>> pywebcopy.config['over_write'] = True

# rest of your code follows..
```

### Changing your project name

By default the pywebcopy creates a directory inside project_folder
with the url you have provided but you can change this using the code 
below

```python
>>> import pywebcopy
>>> pywebcopy.config['project_name'] = 'my_project'

# rest of your code follows..
```

## How to - Save Single Webpage

Particular webpage can be saved easily using the following methods.

Note: if you get `pywebcopy.exceptions.AccessError` when running any of these code then use the code provided on later sections.

### Method 1

Webpage can easily be saved using an inbuilt funtion called `.save_webpage()` which takes several
arguments also.

```python
>>> import pywebcopy
>>> pywebcopy.save_webpage(project_url='http://google.com', project_folder='c://Saved_Webpages/',)

# rest of your code follows..
```

### Method 2

This use case is slightly more powerful as it can provide every functionallity of the WebPage 
data class.

```python
>>> from pywebcopy import Webpage

>>> wp = WebPage('http://google.com', 'e://tests/', project_name='Google')
>>> wp.save_complete()

# This Webpage object contains every methods of the Webpage() class and thus
# can be reused for later usages.

```

### Method 2 using Plain HTML

> :New in version 4.x:

I told you earlier that Webpage object is powerful and can be manipulated in any ways.

One feature is that the raw html is now also accepted.

```python

>>> from pywebcopy import Webpage

>>> HTML = open('test.html').read()

>>> base_url = 'http://example.com' # used as a base for downloading imgs, css, js files.
>>> project_folder = '/saved_pages/'

>>> wp = WebPage(base_url, project_folder, HTML=HTML)
>>> wp.save_webpage()
```

## How to - Whole Websites

Use caution when copying websites as this can overload or damage the
servers of the site and rarely could be illegal, so check everything before
you proceed.

### Method 1 -

Using the inbuilt api `.save_website()` which takes several arguments.

```python
>>> import pywebcopy

>>> pywebcopy.save_website(project_url='http://localhost:8000', project_folder='e://tests/')
```

### Method 2 -

By creating a Crawler() object which provides several other functions as well.

```python
>>> import pywebcopy

>>> pywebcopy.config.setup_config(project_url='http://localhost:5000/', project_folder='e://tests/', project_name='LocalHost')

>>> crawler = pywebcopy.Crawler('http://localhost:5000/')
>>> crawler.crawl()
```

## Contribution

You can contribute in many ways

- reporting bugs on github repo: <https://github.com/rajatomar788/pywebcopy/> or my email.
- creating pull requests on github repo: <https://github.com/rajatomar788/pywebcopy/>
- sending a thanks mail

If you have any suggestions or fixes or reports feel free to mail me :)

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

### 1.3.2 `config.setup_config` Method

>**This function is changed from  `core.setup_config`**

You can manually configure every configuration by using a 
`config.setup_config` call.

```Python

from pywebcopy import config

url = 'http://example-site.com/index.html'
download_loc = 'path/to/downloads/'

pywebcopy.config.setup_config(url, download_loc)

# done!

>>> pywebcopy.config['url']
'http://example-site.com/index.html'

>>> pywebcopy.config['mirrors_dir']
'path/to/downloads'

>>> pywebcopy.config['project_name']
'example-site.com'


## You can also change any of these by just adding param to
## `setup_config` call

>>> pywebcopy.config.setup_config(url, 
        download_loc,project_name='Your-Project', ...)

## You can also change any config even after
## the `setup_config` call

pywebcopy.config.config['url'] = 'http://url-changed.com'
# rest of config remains unchanged

```

Done!

### 1.3.3 List of available `configurations`

below is the list of `config` keys with their `default` values :

```Python
# writes the trace output and log file content to console directly
'DEBUG': False  

# make zip archive of the downloaded content
'zip_project_folder': True

# delete the project folder after making zip archive of it
'delete_project_folder': False

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


# to overwrite the existing files if found
'OVER_WRITE': False

# list of allowed file extensions
'ALLOWED_FILE_EXT': ['.html', '.css', '.json', '.js',
                     '.xml','.svg', '.gif', '.ico',
                      '.jpeg', '.jpg', '.png', '.ttf',
                      '.eot', '.otf', '.woff']

# log file path
'LOG_FILE': None

# name of the mirror project
'PROJECT_NAME': website-name.com

# define the base directory to store all copied sites data
'PROJECT_FOLDER': None


# DANGER ZONE
# CHANGE THESE ON YOUR RESPONSIBILITY
# NOTE: Do not change unless you know what you're doing

# requests headers to be shown on requests made to server
'http_headers': {
    "Accept-Language": "en-US,en;q=0.9",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; PyWebcopyBot/{};) AppleWebKit/604.1.38 (KHTML, like Gecko) Chrome/68.0.3325.162".format(VERSION)
}

# bypass the robots.txt restrictions
'BYPASS_ROBOTS' : False
```

told you there were plenty of `config` vars available!

## 1.5 Undocumented Features

I built many utils and classes in this project to ease
the tasks I was trying to do.

But,
these task are also suitable for general purpose use.

So,
if you want, you can help in generating suitable `documentation` for these undocumented ones, then you can always email me.

## 1.6 Changelog

### [version 5.x]

- Optimization of existing code, upto 5x speed ups in certain cases
- Removed cluttering, improved readability

### [version 4.x]

- *A complete rewrite and restructing of core functionality.*

### [version 2.0.0]

#### [changed]

- `core.setup_config` function is changed to `config.setup_config`.

#### [added]

- added `utils.trace` decorator, which  will **print** *function_name*, *args*, *kwargs* and *return value* when debug config key is True.
- new html-parsers ('html5lib', 'lxml') are supported for better webpages.
- html-parser is now defaulted to 'lxml'. You can use any through new `config.config` key called `parser`

#### [fixed]

- fixed issue while changing `user-agent` key cracked webpages. You can now use any browser's user-agent id and it will get exact same page downloaded.
- fixed issue in `generators.extract_css_urls` which was caused by `str` and `bytes` difference in python3.
- fixed issues in modules importing. (Thanks "**Илья Игоревич**").
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
