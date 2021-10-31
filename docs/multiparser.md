## MultiParser Scraping

Multiple scraping packages are wrapped up in one object 
which you can use to unlock the best of all those libraries
at one go without having to go through the hassle of 
separately interacting with each one of those libraries.

> To use all the methods and properties documented below
> just create a object once as described

```python
from pywebcopy.parsers import MultiParser

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
