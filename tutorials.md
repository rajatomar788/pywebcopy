# Tutorials for sample use-cases with pywebcopy

This modules demos some general use cases when
working with pywebcopy.

## First steps

You should always check if the pywebcopy is installed successfully.

```python
>>> import pywebcopy
>>> pywebcopy.__version___
5.x
```

Your version may be different, now you can continue the tutorial.

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
