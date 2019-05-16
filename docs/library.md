
### `WebPage` class

`WebPage` class, the engine of this saving actions.
You can use this class to access many more methods to
customise the process with.

- Creating the instance

    You can directly import this class from `pywebcopy` package.
    
        from pywebcopy import WebPage    
        wp = WebPage()
    

- fetching the html source from internet
   
   You can tell it to fetch the source from the
   internet, it then uses `requests` module to fetch it
   for you.
   
   You can pass in the several `params`
   which `requests.get()` would accept 
   e.g. *proxies, auth etc.*
   
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
        
    
- providing your own opened file
    You can also provide opened source handles
    directly 
    
        from pywebcopy import WebPage    
        wp = WebPage()
        
        # You can choose to set the source yourself
        handle = open('file.html', 'rb')
        wp.set_source(handle)
            
    
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

        from pywebcopy import WebPage
        wp = WebPage()
        wp.get('http://google.com')
    
        wp.save_html()
        #> a `html` file would be saved at
   

- `.save_html` method
    After setting up the `WebPage` instance you can
    use this method to save a local copy of the parsed
    and modified html at `.file_path` property value.
    
        from pywebcopy import WebPage
        wp = WebPage()
        wp.get('http://google.com')
    
        wp.save_html()
        #> a .html file would be saved at location which
        #> `.file_path` property returns

- `.save_complete` method
    This is the important api which you would be using
    frequently for saving or cloning a webpage for later
    reading or whatever the use case would be.

    This methods saves all the `css`, `js`, `images`, `fonts` etc.
    in the same order as a most browser would do when you will click on
    the `save page` option in the right click menu.

    if you want complete webpage with css, js and 
    images

        from pywebcopy import WebPage
        wp = WebPage()
        wp.get('http://google.com')
    
        wp.save_complete()


## 3.1 Scrapings Support

Multiple scraping packages are wrapped up in one object 
which you can use to unlock the best of all those libraries
at one go without having to go through the hassle of 
instanciating each one of those libraries

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

- #### BeautifulSoup methods are supported
    you can also use any beautiful_soup methods on it
    
        >>> links = wp.bs4.find_all('a')
        
        ['//docs.python.org/3/tutorial/', '/about/apps/', 
        'https://github.com/python/pythondotorg/issues', '
        /accounts/login/', '/download/other/']
    

-   #### `lxml` is completely supported
    
    You can use any lxml methods on it. Read more about lxml at `http://lxml.de/`
    
        >>> wp.lxml.xpath('//a', ..)
        [<Element 'a'>,<Element 'a'>]


- #### `pyquery` is Fully supported
    
    You can use PyQuery methods on it .Read more about pyquery at 
    
        >>> wp.pq.select(selector, ..)
        [https://pythonhosted.org/pyquery/]


-   #### `lxml.xpath` is also supported
    
    xpath is also natively supported which retures a :class: `requests_html.Element`
    See more at `https://html.python-requests.org`

        >>> wp.xpath('a')
        ['<Element 'a' class='btn'
         href='https://help.github.com/articles/supported-browsers'>'
         ]

    
-   #### select only elements containing certain text
    
    Provided through the `requests_html` module.

        >>> wp.find('a', containing='kenneth')
        [<Element 'a' href='http://kennethreitz.com/pages'>, ...]


## `Crawler` class in `pywebcopy`
Class on which website cloning depends upon.
