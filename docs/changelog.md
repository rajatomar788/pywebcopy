## Contribution

You can contribute in many ways

- give it a star on github repo
- reporting bugs on github repo: <https://github.com/rajatomar788/pywebcopy/> or at my email.
- creating pull requests on github repo: <https://github.com/rajatomar788/pywebcopy/>
- sending a thanks mail

If you have any suggestions or fixes or reports feel free to mail me :)

## Undocumented Features

I built many utils and classes in this project to ease
the tasks I was trying to do.
But these classes are also suitable for general purpose use.

So,
if you want, you can help in generating suitable `documentation` for these undocumented ones,
then you can always create and pull request or email me.

## Changelog

### [version 7.0.0]
- Object-oriented rewrite of the `pywebcopy`
- command line interface is improved.
- better reliability when using threading.
- separate modes for threaded and non-threaded tasks.

### [version 6.0.0]

- `WebPage` class now doesn't take any argument **(breaking change)**
- `WebPage` class has new methods `WebPage.get` and `WebPage.set_source`
- Queuing of downloads is replaced with a barrier to manage active threads


### [version 5.x]

- Optimization of existing code, upto 5x speed ups in certain cases
- Removed cluttering, improved readability

### [version 4.x]

- **A complete rewrite and restructing of apis.**
- Availble apis through `from pywebcopy import *`

    * `save_webpage` 
    * `save_website`                            
    * `config`         
    * `WebPage` 
    * `Crawler` 
    * `MultiParser`      
    * `SESSION`    
    * `URLTransformer` 
    * `filename_present`                    
    * `TagBase` 
    * `LinkTag` 
    * `ScriptTag` 
    * `ImgTag` 
    * `AnchorTag` 
    * `get` 
    * `new_file`

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
