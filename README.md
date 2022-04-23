```
    ____       _       __     __    ______                     _____   
   / __ \__  _| |     / /__  / /_  / ____/___  ____  __  __   /__  /   
  / /_/ / / / / | /| / / _ \/ __ \/ /   / __ \/ __ \/ / / /     / /    
 / ____/ /_/ /| |/ |/ /  __/ /_/ / /___/ /_/ / /_/ / /_/ /     / /     
/_/    \__, / |__/|__/\___/_.___/\____/\____/ .___/\__, /     /_/      
      /____/                               /_/    /____/               
```

`Created By : Raja Tomar`
`License : Apache License 2.0`
`Email: rajatomar788@gmail.com`
[![Downloads](https://pepy.tech/badge/pywebcopy)](https://pepy.tech/project/pywebcopy)


PyWebCopy is a free tool for copying full or partial websites locally
onto your hard-disk for offline viewing.

PyWebCopy will scan the specified website and download its content onto your hard-disk.
Links to resources such as style-sheets, images, and other pages in the website
will automatically be remapped to match the local path.
Using its extensive configuration you can define which parts of a website will be copied and how.

## What can PyWebCopy do?

PyWebCopy will examine the HTML mark-up of a website and attempt to discover all linked resources
such as other pages, images, videos, file downloads - anything and everything.
It will download all of theses resources, and continue to search for more.
In this manner, WebCopy can "crawl" an entire website and download everything it sees
in an effort to create a reasonable facsimile of the source website.

## What can PyWebCopy not do?

PyWebCopy does not include a virtual DOM or any form of JavaScript parsing.
If a website makes heavy use of JavaScript to operate, it is unlikely PyWebCopy will be able
to make a true copy if it is unable to discover all of the website due to
JavaScript being used to dynamically generate links.

PyWebCopy does not download the raw source code of a web site,
it can only download what the HTTP server returns.
While it will do its best to create an offline copy of a website,
advanced data driven websites may not work as expected once they have been copied.

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
7.x.x
```

Your version may be different, now you can continue the tutorial.

## Basic Usages

To save any single page, just type in python console

```python

from pywebcopy import save_webpage
save_webpage(
      url="https://httpbin.org/",
      project_folder="E://savedpages//",
      project_name="my_site",
      bypass_robots=True,
      debug=True,
      open_in_browser=True,
      delay=None,
      threaded=False,
)

```

To save full website (This could overload the target server, So, be careful)

```Python

from pywebcopy import save_website
save_website(
url="https://httpbin.org/",
project_folder="E://savedpages//",
project_name="my_site",
bypass_robots=True,
debug=True,
open_in_browser=True,
delay=None,
threaded=False,
)

```

### Running Tests
Running tests is simple and doesn't require any external library. 
Just run this command from root directory of pywebcopy package.


```shell
$ python -m pywebcopy --tests
```



### Command Line Interface
`pywebcopy` have a very easy to use command-line interface which
can help you do task without having to worrying about the inner
long way.

- #### Getting list of commands
    ```shell
    $ python -m pywebcopy --help
    ```
- #### Using CLI
  ```
  Usage: pywebcopy [-p|--page|-s|--site|-t|--tests] [--url=URL [,--location=LOCATION [,--name=NAME [,--pop [,--bypass_robots [,--quite [,--delay=DELAY]]]]]]]
  
  Python library to clone/archive pages or sites from the Internet.
  
  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    --url=URL             url of the entry point to be retrieved.
    --location=LOCATION   Location where files are to be stored.
    -n NAME, --name=NAME  Project name of this run.
    -d DELAY, --delay=DELAY
                          Delay between consecutive requests to the server.
    --bypass_robots       Bypass the robots.txt restrictions.
    --threaded            Use threads for faster downloading.
    -q, --quite           Suppress the logging from this library.
    --pop                 open the html page in default browser window after
                          finishing the task.
  
    CLI Actions List:
      Primary actions available through cli.
  
      -p, --page          Quickly saves a single page.
      -s, --site          Saves the complete site.
      -t, --tests         Runs tests for this library.
  
  
  ```
- #### Running tests
  ```shell
    $ python -m pywebcopy run_tests
  ```


### Authentication and Cookies
Most of the time authentication is needed to access a certain page.
Its real easy to authenticate with `pywebcopy` because it uses an 
`requests.Session` object for base http activity which can be accessed 
through `WebPage.session` attribute. And as you know there
are ton of tutorials on setting up authentication with `requests.Session`.

Here is an example to fill forms

```python
from pywebcopy.configs import get_config

config = get_config('http://httpbin.org/')
wp = config.create_page()
wp.get(config['project_url'])
form = wp.get_forms()[0]
form.inputs['email'].value = 'bar' # etc
form.inputs['password'].value = 'baz' # etc
wp.submit_form(form)
wp.get_links()

```


You can read more in the github repositories `docs` folder.