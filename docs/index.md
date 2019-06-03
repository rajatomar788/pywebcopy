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
$ python -m unittest tests
```



### Command Line Interface
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


### Authentication and Cookies
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
