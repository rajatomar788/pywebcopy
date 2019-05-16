# PyWebCopy &copy; 6

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
    * beautifulsoup4
    * lxml
    * requests
    * requests_html
    * pyquery

Email me at `rajatomar788@gmail.com` of any query :)

## Installation

`pywebcopy` is available on PyPi and is easily installable using `pip`

```shell

$ pip install pywebcopy

```

You are ready to go. Read the tutorials below to get started.

## First steps

You should always check if the latest pywebcopy is installed successfully.

```pydocstring
>>> import pywebcopy
>>> pywebcopy.__version___
6.0.0
```

Your version may be different, now you can continue the tutorial.

## Basic Usages

To save any single page, just type in python console

```pydocstring
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

### Running Tests
Running tests is simple and doesn't require any external library. 
Just run this command from root directory of pywebcopy package.


```shell
$ python -m unittest pywebcopy.tests
```

