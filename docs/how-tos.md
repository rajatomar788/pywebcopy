## How to - Save Single Webpage

Particular webpage can be saved easily using the following methods.

_Note:_ if you get `pywebcopy.exceptions.AccessError` 
when running any of these code then use the code provided on later sections.

### Method 1 : via api - `save_webpage()`

Webpage can easily be saved using an inbuilt funtion called `.save_webpage()` which takes several
arguments also.

```pydocstring
>>> from pywebcopy import save_webpage
>>> save_webpage(project_url='http://google.com', project_folder='c://Saved_Webpages/',)
```

### Method 2

This use case is slightly more powerful as it can provide every functionallity of the WebPage class.

```pydocstring
>>> from pywebcopy import WebPage, config
>>> url = 'http://some-url.com/some-page.html'

# You should always start with setting up the config or use apis
>>> config.setup_config(url, project_folder, project_name, **kwargs)

# Create a instance of the webpage object
>>> wp = Webpage()

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

### Method 2 (using Plain HTML)

I told you earlier that Webpage object is powerful and can be manipulated in any ways.

One feature is that the raw html is now also accepted.

```pydocstring

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

```pydocstring
>>> from pywebcopy import save_website

>>> save_website(project_url='http://localhost:8000', project_folder='e://tests/')

```

### Method 2 - `Crawler` class 

By creating a Crawler() object which provides several other functions as well.

```pydocstring
>>> from pywebcopy import Crawler, config

>>> config.setup_config(project_url='http://localhost:5000/', project_folder='e://tests/', project_name='LocalHost')

>>> crawler = Crawler('http://localhost:5000/')
>>> crawler.crawl()

```