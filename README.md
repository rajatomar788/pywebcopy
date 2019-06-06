# PyWebCopy &copy; 6

[![PyPI](https://img.shields.io/pypi/v/pywebcopy.svg)](https://pypi.org/project/pywebcopy/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pywebcopy.svg?color=green)](https://pypi.org/project/pywebcopy/)
[![PyPI - Status](https://img.shields.io/pypi/status/pywebcopy.svg?color=9cf)](https://pypi.org/project/pywebcopy/)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/e8e86b7187f6443abfcf7d943d2e7cca)](https://app.codacy.com/app/rajatomar788/pywebcopy?utm_source=github.com&utm_medium=referral&utm_content=rajatomar788/pywebcopy&utm_campaign=Badge_Grade_Dashboard)

`Created By : Raja Tomar`
`License : MIT`
`Email: rajatomar788@gmail.com`

Python websites and webpages cloning at ease.
Web Scraping or Saving Complete webpages and websites with python.

Web scraping and archiving tool written in Python
Archive any online website and its assets, css, js and
images for offilne reading, storage or whatever reasons.
It's easy with `pywebcopy`.

Why it's great? because it -

- respects `robots.txt`
- saves a webpage with css, js and images with one call
- clones a complete website with assets and links remapped in one call
- have direct apis for simplicity and ease
- subclassing for advanced usage
- custom html tags handler support
- lots of configuration for many custom needs
- provides several scraping packages in one objects for scraping under one class
  - lxml
  - requests
  - beautifulsoup4
  - pyquery
  - requests_html

Email me at `rajatomar788@gmail.com` of any query :)

## 1.1 Installation

`pywebcopy` is available on PyPi and is easily installable using `pip`

```shell

$ pip install pywebcopy

```

You are ready to go. Read the tutorials below to get started.

## 1.1.1 First steps

You should always check if the latest pywebcopy is installed successfully.

```python
>>> import pywebcopy
>>> pywebcopy.__version___
6.0.0

```

Your version may be different, now you can continue the tutorial.

## 1.2 Basic Usages

To save any single page, just type in python console

```Python
from pywebcopy import save_webpage

kwargs = {'project_name': 'some-fancy-name'}

save_webpage(
    url='http://example-site.com/index.html',
    project_folder='path/to/downloads',
    **kwargs
)

```

To save full website (This could overload the target server, So, be careful)

```Python

from pywebcopy import save_website

kwargs = {'project_name': 'some-fancy-name'}

save_website(
    url='http://example-site.com/index.html',
    project_folder='path/to/downloads',
    **kwargs
)

```

### 1.3 Running Tests
Running tests is simple and doesn't require any external library. 
Just run this command from root directory of pywebcopy package.


```shell
$ python -m pywebcopy run-tests
```

### 1.4 Command Line Interface
`pywebcopy` have a very easy to use command-line interface which
can help you do task without having to worrying about the inner
long way.
- #### Getting list of commands
    ```shell
    $ python -m pywebcopy -- --help
    ```
- #### Using apis
    ```shell
    $ python -m pywebcopy save_webpage http://google.com E://store// --bypass_robots=True
    or
    $ python -m pywebcopy save_website http://google.com E://store// --bypass_robots
    ``` 
- #### Running tests
    ```shell
    $ python -m pywebcopy run_tests
    ```


### 1.5 Authentication and Cookies
Most of the time authentication is needed to access a certain page.
Its real easy to authenticate with `pywebcopy` because it usage an 
`requests.Session` object for base http activity which can be accessed 
through `pywebcopy.SESSION` attribute. And as you know there
are ton of tutorials on setting up authentication with `requests.Session`.

Here is a basic example of simple http auth -
```python
import pywebcopy

# Update the headers with suitable data

pywebcopy.SESSION.headers.update({
    'auth': {'username': 'password'},
    'form': {'key1': 'value1'},
})

# Rest of the code is as usual
kwargs = {
    'url': 'http://localhost:5000',
    'project_folder': 'e://saved_pages//',
    'project_name': 'my_site'
}
pywebcopy.config.setup_config(**kwargs)
pywebcopy.save_webpage(**kwargs)

```


### 2.1 `WebPage` class

`WebPage` class, the engine of this saving actions.
You can use this class to access many more methods to
customise the process with.

- Creating the instance

    You can directly import this class from `pywebcopy` package.
    
    ```Python
    from pywebcopy import WebPage    
    wp = WebPage()
    ```

- fetching the html source from internet
   
   You can tell it to fetch the source from the
   internet, it then uses `requests` module to fetch it
   for you.
   
   You can pass in the several `params`
   which `requests.get()` would accept 
   e.g. *proxies, auth etc.*
   
   ```python
    from pywebcopy import WebPage    
    wp = WebPage()
  
    # You can choose to load the page explicitly using 
    # `requests` module with params `requests` would take
  
    url = 'http://google.com'
    params = {
        'auth': 'username@password',
        'proxies': 'localhost:5000',
    }
    wp.get(url, **params)
    ```
    
- providing your own opened file
    You can also provide opened source handles
    directly 
    
    ```Python
    from pywebcopy import WebPage    
    wp = WebPage()
    
    # You can choose to set the source yourself
    handle = open('file.html', 'rb')
    wp.set_source(handle)
    ```
    
### 2.1.2  `WebPage` properties and methods

Apis which `WebPage` object exposes after creating
through any method described above

- `.file_path` property
    **Read-only** location at which this file will end up 
    when you try to save the parsed html source
    
    To change this location you have to manipulate the
    `.utx` property of the `WebPage` class. You can
    look it up below.


- `.project_path` property
    **Read-only** location at which all the files will end up 
    when you try to save the complete webpage.
    
    To change this location you have to manipulate the
    `.utx` property of the `WebPage` class. You can
    look it up below.


- `.save_assets` method
    This methods saves all the `css`, `js`, `images`, `fonts` etc.
    in the folder you setup through property `.project_path`.

    ```Python

    from pywebcopy import WebPage
    wp = WebPage()
    wp.get('http://google.com')

    wp.save_html()
    #> a .html file would be saved at
    ```


- `.save_html` method
    After setting up the `WebPage` instance you can
    use this method to save a local copy of the parsed
    and modified html at `.file_path` property value.

    ```Python

    from pywebcopy import WebPage
    wp = WebPage()
    wp.get('http://google.com')

    wp.save_html()
    #> a .html file would be saved at location which
    #> `.file_path` property returns
    ```

- `.save_complete` method
    This is the important api which you would be using
    frequently for saving or cloning a webpage for later
    reading or whatever the use case would be.

    This methods saves all the `css`, `js`, `images`, `fonts` etc.
    in the same order as a most browser would do when you will click on
    the `save page` option in the right click menu.

    if you want complete webpage with css, js and images
    ```Python
    from pywebcopy import WebPage
    wp = WebPage()
    wp.get('http://google.com')

    wp.save_complete()
    ```

## 3.1 Scrapings Support

Multiple scraping packages are wrapped up in one object 
which you can use to unlock the best of all those libraries
at one go without having to go through the hassle of 
instantiating each one of those libraries

> To use all the methods and properties documented below
> just create a object once as described

```python
from pywebcopy import MultiParser

import requests

req = requests.get('http://google.com')

html = req.content

# You can skip the encoding declaration
# it is start enough to auto-detect :)
encoding = req.encoding

wp = MultiParser(html, encoding)

# done

```

> All code follows above code

-    #### BeautifulSoup methods are supported
    
    you can also use any beautiful_soup methods on it
    
    ```python
    >>> links = wp.bs4.find_all('a')
    
    ['//docs.python.org/3/tutorial/', '/about/apps/', 'https://github.com/python/pythondotorg/issues', '/accounts/login/', '/download/other/']
    
    ```

-   #### `lxml` is completely supported
    
    You can use any lxml methods on it. Read more about lxml at `http://lxml.de/`
    
    ```python
    >>> wp.lxml.xpath('//a', ..)
    [<Element 'a'>,<Element 'a'>]
    
    ```

- #### `pyquery` is Fully supported
    
    You can use PyQuery methods on it .Read more about pyquery at `https://pythonhosted.org/pyquery/`
    
    ```python
    >>> wp.pq.select(selector, ..)
    ...
    ```

-   #### `lxml.xpath` is also supported
    
    xpath is also natively supported which retures a :class: `requests_html.Element`
    See more at `https://html.python-requests.org`
    
    ```python
    
    >>> wp.xpath('a')
    ['<Element 'a' class='btn' href='https://help.github.com/articles/supported-browsers'>']
    ```
    
-   #### select only elements containing certain text
    
    Provided through the `requests_html` module.
    
    ```python
    >>> wp.find('a', containing='kenneth')
    >>> [<Element 'a' href='http://kennethreitz.com/pages'>, ...]
    ```

## `Crawler` object
This is a subclass of `WebPage` class and can be used to mirror any website.

```python
>>> from pywebcopy import Crawler, config
>>> url = 'http://some-url.com/some-page.html'
>>> project_folder = '/home/desktop/'
>>> project_name = 'my_project'
>>> kwargs = {'bypass_robots': True}
# You should always start with setting up the config or use apis
>>> config.setup_config(url, project_folder, project_name, **kwargs)

# Create a instance of the webpage object
>>> wp = Crawler()

# If you want to you can use `requests` to fetch the pages
>>> wp.get(url, **{'auth': ('username', 'password')})

# Then you can access several methods like
>>> wp.crawl()

```


## Common Settings and Errors

You can easily make a beginners mistake or could get confuse,
thus here are the common errors and how to correct them if you
are facing them. 

1. `pywebcopy.exceptions.AccessError`

    If you are getting `pywebcopy.exceptions.AccessError` Exception.
    then check if website allows scraping of its content.
    
    ```python
    >>> import pywebcopy
    >>> pywebcopy.config['bypass_robots'] = True
    
    # rest of your code follows..
    
    ```

2. Overwrite existing files when copying
    
    If you want to overwrite existing files in the directory then
    use the over_write config key.
    
    ```python
    
    import pywebcopy
    pywebcopy.config['over_write'] = True
    
    # rest of your code follows..
    
    ```

3. Changing your project name
    
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

### Method 1 : via api - `save_webpage()`

Webpage can easily be saved using an inbuilt funtion called `.save_webpage()` which takes several
arguments also.

```python
>>> from pywebcopy import save_webpage
>>> save_webpage(project_url='http://google.com', project_folder='c://Saved_Webpages/',)

```

### Method 2

This use case is slightly more powerful as it can provide every functionallity of the WebPage class.

```python
>>> from pywebcopy import WebPage, config
>>> url = 'http://some-url.com/some-page.html'

# You should always start with setting up the config or use apis
>>> config.setup_config(url, project_folder, project_name, **kwargs)

# Create a instance of the webpage object
>>> wp = WebPage()

# If you want to use `requests` to fetch the page then
>>> wp.get(url)

# Else if you want to use plain html or urllib then use
>>> wp.set_source(object_which_have_a_read_method, encoding=encoding)
>>> wp.url = url   # you need to do this if you are using set_source()

# Then you can access several methods like
>>> wp.save_complete()
>>> wp.save_html()
>>> wp.save_assets()

# This Webpage object contains every methods of the Webpage() class and thus
# can be reused for later usages.

```

### Method 2 using Plain HTML

I told you earlier that Webpage object is powerful and can be manipulated in any ways.

One feature is that the raw html is now also accepted.

```python

>>> from pywebcopy import WebPage, config

>>> HTML = open('test.html').read()

>>> base_url = 'http://example.com' # used as a base for downloading imgs, css, js files.
>>> project_folder = '/saved_pages/'
>>> config.setup_config(base_url, project_folder)

>>> wp = WebPage()
>>> wp.set_source(HTML)
>>> wp.url = base_url
>>> wp.save_webpage()

```

## How to - Clone Whole Websites

Use caution when copying websites as this can overload or damage the
servers of the site and rarely could be illegal, so check everything before
you proceed.

### Method 1 : via api - `save_website()`

Using the inbuilt api `.save_website()` which takes several arguments.

```python
>>> from pywebcopy import save_website

>>> save_website(project_url='http://localhost:8000', project_folder='e://tests/')

```

### Method 2 -

By creating a Crawler() object which provides several other functions as well.

```python
>>> from pywebcopy import Crawler, config

>>> config.setup_config(project_url='http://localhost:5000/', 
project_folder='e://tests/', project_name='LocalHost')

>>> crawler = Crawler()
>>> crawler.crawl()

```

## 1.3 Configuration

`pywebcopy` is highly configurable. You can setup the global object
using the methods exposed by the `pywebcopy.config` object.

Ways to change the global configurations are below -

- Using the method `.setup_config`  on global `pywebcopy.config` object

    You can manually configure every configuration by using a 
    `.setup_config` call.

    ```Python

    >>> import pywebcopy

    >>> url = 'http://example-site.com/index.html'
    >>> download_loc = 'path/to/downloads/'
    >>> project = 'my_project'

    >>> pywebcopy.config.setup_config(url, download_loc, project, **kwargs)
    # done!

    # Now check
    >>> pywebcopy.config.get('project_url')
    'http://example-site.com/index.html'

    >>> pywebcopy.config.get('project_folder')
    'path/to/downloads'

    >>> pywebcopy.config.get('project_name')
    'example-site.com'

    ## You can also change any config even after
    ## the `setup_config` call

    pywebcopy.config['url'] = 'http://url-changed.com'
    # rest of config remains unchanged


    Done!

- Passing in the config vars directly to the 

    global apis e.g. `.save_webpage`

    To change any configuration, just pass it to the `api` call.

    Example:

    ```Python
    from pywebcopy import save_webpage

    kwargs = {
        'project_url': 'http://google.com',
        'project_folder': '/home/pages/',
        'project_name': 
        ...
    }

    save_webpage(**kwargs)

    ```

    #### List of available `configurations`

    below is the list of `config` keys with their `default` values :

    ```Python

    # writes the trace output and log file content to console directly
    'DEBUG': False  

    # make zip archive of the downloaded content
    'zip_project_folder': True

    # delete the project folder after making zip archive of it
    'delete_project_folder': False

    # to download css file or not
    'LOAD_CSS': True

    # to download images or not
    'LOAD_IMAGES': True

    # to download js file or not
    'LOAD_JAVASCRIPT': True


    # to overwrite the existing files if found
    'OVER_WRITE': False

    # list of allowed file extensions
    # shortend for readability
    'ALLOWED_FILE_EXT': ['.html', '.css', ...]

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
    'http_headers': {...}

    # bypass the robots.txt restrictions
    'BYPASS_ROBOTS' : False

    ```

## 4.1 Contribution

You can contribute in many ways

- give it a star on github repo
- reporting bugs on github repo: <https://github.com/rajatomar788/pywebcopy/> or at my email.
- creating pull requests on github repo: <https://github.com/rajatomar788/pywebcopy/>
- sending a thanks mail

If you have any suggestions or fixes or reports feel free to mail me :)

## 5.1 Undocumented Features

I built many utils and classes in this project to ease
the tasks I was trying to do.

But,
these task are also suitable for general purpose use.

So,
if you want, you can help in generating suitable `documentation` for these undocumented ones,
then you can always create and pull request or email me.

## 6.1 Changelog

### [version 6.0.0]
- **Breaking Change** New command-line interface using `Python Fire` library.
- Implemented type checks and path normalising in the `config.setup_paths`.
- added new dynamic `pywebcopy.__all__` attr generation.
- `WebPage` class now doesnt take any argument **(breaking change)**
- `WebPage` class has new methods `WebPage.get` and `WebPage.set_source`
- Queuing of downloads is replaced with a barrier to manage active threads


### [version 5.x]

- Optimization of existing code, upto 5x speed ups in certain cases
- Removed cluttering, improved readability

### [version 4.x]

- *A complete rewrite and restructuring of core functionality.*

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
