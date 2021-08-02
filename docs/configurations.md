## Configuring pywebcopy

`pywebcopy` is highly configurable. You can setup the global object
using the methods exposed by the `pywebcopy.config` object.

Ways to change the global configurations are below -

- Using the method `.setup_config`  on global `pywebcopy.config` object

    You can manually configure every configuration by using a 
    `.setup_config` call.
    
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
    
            from pywebcopy import save_webpage
    
            kwargs = {
                'project_url': 'http://google.com',
                'project_folder': '/home/pages/',
                'project_name': 
                ...
            }
        
            save_webpage(**kwargs)
        
#### List of available `configurations`
    
below is the list of `config` keys with their `default` values :

```yaml

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
    'ALLOWED_FILE_EXT': {'.html', '.css', ...}

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

## Common Settings and Errors

You can easily make a beginners mistake or could get confuse,
thus here are the common errors and how to correct them if you
are facing them. 

1. `pywebcopy.exceptions.AccessError`

    If you are getting `pywebcopy.exceptions.AccessError` Exception.
    then check if website allows scraping of its content.

        >>> import pywebcopy
        >>> pywebcopy.config['bypass_robots'] = True
        
        # rest of your code follows..


2. Overwrite existing files when copying
    
    If you want to overwrite existing files in the directory then
    use the over_write config key.

        import pywebcopy
        pywebcopy.config['over_write'] = True
        
        # rest of your code follows..


3. Changing your project name
    
    By default the pywebcopy creates a directory inside project_folder
    with the url you have provided but you can change this using the code 
    below

        >>> import pywebcopy
        >>> pywebcopy.config['project_name'] = 'my_project'
    
        # rest of your code follows..
        

