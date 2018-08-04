# -*- coding: utf-8 -*-

"""
aerwebcopy.core
~~~~~~~~~~~~~~~

* DO NOT TOUCH *

Core of the aerwebcopy engine.
"""

from __future__ import print_function

import datetime
import shutil
import sys

import bs4
import requests

py2 = True if sys.version_info.major == 2 else False
py3 = True if sys.version_info.major == 3 else False

from generators import *
from utils import *
import config as cfg

import zipfile
import os
import re


if py2:
    import robotparser
    import urlparse
elif py3:
    from urllib import robotparser
    from urllib import parse as urlparse


__all__ = [
    'py3', 'py2', 'init', 'get', 'watermark', 'now', 'save_webpage', 'crawl'
]


# -----------------------------------------------------
# function which sets up defaults and dirs to work with
# then fires up the main engines
# -----------------------------------------------------
def init(url, **kwargs):

    # if external configuration is provided then use it
    cfg.config.update(kwargs)
    # set required configurations
    
    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        'User-Agent': cfg.config['USER_AGENT']
    }
    # check if the provided url works
    _dummy_request = requests.get(url, headers=headers)

    if not _dummy_request.ok:
        print("error :: Provided URL %s didn't work!" % url)
        sys.exit()

    # Assign the resolved or found url so that it doesnot generate
    # error of redirection request
    cfg.config['URL'] = _dummy_request.url
    
    cfg.config['PROJECT_NAME'] = cfg.config['PROJECT_NAME'] or netloc_without_port(
        cfg.config['URL'])
    cfg.config['MIRRORS_DIR'] = cfg.config['MIRRORS_DIR'] or os.path.abspath(os.path.join(
        'C:\\', 'WebCopyProjects', cfg.config['PROJECT_NAME']))
    cfg.config['LOG_FILE'] = cfg.config['LOG_FILE'] or os.path.join(
        cfg.config['MIRRORS_DIR'], cfg.config['PROJECT_NAME'] + '_log.txt')
    cfg.config['LINK_INDEX_FILE'] = cfg.config['LINK_INDEX_FILE'] or os.path.join(
        cfg.config['MIRRORS_DIR'], '%s_indexed_links.txt' % cfg.config['PROJECT_NAME'])
    # initialise the robots parser so that we don't overrun websites
    # with copyright policies
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(cfg.config['URL'], '/robots.txt'))
    rp.read()
    cfg.config['ROBOTS'] = rp

    # create work dirs if it do not exists
    if not os.path.exists(cfg.config['MIRRORS_DIR']):
        os.makedirs(cfg.config['MIRRORS_DIR'])

    # delete all the log in logfile and start afresh
    open(cfg.config['LOG_FILE'], 'w+').truncate()

    now(
        '\n\nInitialising the Script with following Configuration Set: \n%s \n \n' % '\n\n'.join(
            str(cfg.config).strip('\{\}').split(', ')),
        level=1,
        compressed=False
    )

    try:
        # start the crawler
        crawl(cfg.config['URL'])

    except KeyboardInterrupt:
        now('Stopped Crawler!', to_console=True)
        now('Finishing Up...', to_console=True)

    finally:
        """Print Useful information about completed project to 
            python console.
        """
        print('')
        now(
            "Downloaded Content :: %s KB's" % str(
                cfg.config['DOWNLOAD_SIZE'] // 1024),
            to_console=True
        )
        now(
            'Downloaded Files :: \n%s' % '\n'.join(cfg.config['DOWNLOADED_FILES'])
        )
        
        # writes the buffered log to external file
        # if buffering was on
        if cfg.config['LOG_BUFFERING']:

            with open(cfg.config['LOG_FILE'], 'a+') as log_file:
                log_file.write(
                    '\n\n'.join(cfg.config['LOG_BUFFER_ARRAY'])
                )

        if cfg.config['MAKE_ARCHIVE']:
            
            # NOTE: Old Method, a one-liner
            '''_archive = shutil.make_archive(
                os.path.abspath(cfg.config['MIRRORS_DIR']), 'zip',
                root_dir=os.path.abspath(cfg.config['MIRRORS_DIR'])
            )'''

            # new method, less error prone
            # make zip archive of all the files
            archive = zipfile.ZipFile(
                os.path.abspath(cfg.config['MIRRORS_DIR']) + '.zip', 'w', zipfile.ZIP_DEFLATED
            )

            for foldername, subfolders, filenames in os.walk(cfg.config['MIRRORS_DIR']):

                # add current folder to zip file
                try:
                    #archive.write(foldername)
                    pass
                except:
                    now("Folder %s generated %s error while adding to archive." % (foldername, e.message), level=3)
                
                for filename in filenames:
                    if filename.endswith('.zip'):
                        continue
                    try:
                        _temp_filename = os.path.join(foldername, filename)
                        archive.write(_temp_filename, _temp_filename[len(cfg.config['mirrors_dir']):])
                    except Exception as e:
                        now("File %s generated %s error while adding to archive." % (foldername, e.message), level=3)
                    
            archive.close()
                        
            now('Saved the Project as ZIP archive at %s' %  (cfg.config['MIRRORS_DIR'] + '.zip'),
                to_console=True
                )

        # delete the temp folder after making archive
        if cfg.config['CLEAN_UP']:
            # clean up the mirrors dir
            
            print('Cleaning up %s' % cfg.config['MIRRORS_DIR'])
                
            shutil.rmtree(cfg.config['MIRRORS_DIR'])

        # ALL DONE
        print("All Done!")


# ---------------------------------------------------------
# toolkit func to make requests using custom configs
# it returns request content if request was successful
# None otherwise.
# ---------------------------------------------------------
def get(url):
    """func returns the fetched data from internet
        using a popular python library called `requests`

    :params url: the url of the page or file to be fetched
    """

    # check if website allows bot access
    if not cfg.config['ROBOTS'].can_fetch("*", url) and not cfg.config['BYPASS_ROBOTS']:

        now(
            "error :: Website doesn't allow access to the url %s" % url,
            to_console=True,
            level=3
        )
        return

    elif not cfg.config['ROBOTS'].can_fetch("*", url) and cfg.config['BYPASS_ROBOTS']:
        now(
            'forced :: Accessing restricted website part %s' % url,
            to_console=True,
            level=4
        )

    else:
        now(
            "allowed :: Website allows access to the url %s" % url,
            to_console=True,
            level=2
        )

    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        'User-Agent': cfg.config['USER_AGENT']
    }

    # this returns a request object fetched through the module
    try:
        
        # make request to page
        req = requests.get(url, headers=headers)
        # log downloaded filesize
        cfg.config['DOWNLOAD_SIZE'] += int(req.headers.get('content-length', 0))
        return req

    except requests.exceptions.ConnectionError:
        now(
            'error :: Internet Connection not Found!',
            level=4,
            to_console=True
        )
        return

    except requests.exceptions.InvalidSchema:
        now(
            'error :: Invalid Schema',
            level=4,
            to_console=True
        )
        return


# -----------------------------------------------------------
# toolkit func to generate a file with filename and data
# it checks various expects before creating a file
# but it is as easy as `new_file('pathtofile', 'filecontent')`
# -----------------------------------------------------------
def new_file(file_path, content=None, url=None):

    """if filename contains unsupported file or folder names by os

    Example:
        filename = 'path/to/file?args=value#fragments

    it will try to generate a valid file path otherwise
    then we will have to skip downloading of this file
    because even if we download it anyways then
    windows will refuse to store it
    """

    global _mime_type
    print()

    now('fetching :: %s' % file_path, to_console=True)

    try:
        # create a compatible path for file to be stored easily
        file_path = generate_path_for(file_path)

    except TypeError:
        now(
            'error :: file type %s is not valid' % file_path,
            level=4,
            to_console=True
        )
        return

    # this ensure that url is not a base64 encoded content
    if not file_path_is_valid(file_path):
        now(
            'error :: file type %s is not valid' % file_path,
            level=4,
            to_console=True
        )
        return

    # if file of this type is allowed to be saved
    if not os.path.splitext(file_path)[1] in cfg.config['ALLOWED_FILE_EXT']:
        now(
            'error :: file of type %s is not allowed!'
            % str(os.path.splitext(file_path)[1]),
            level=3,
            to_console=True
        )
        return

    # if newly created file_path already a file
    if os.path.exists(file_path):

        now('exists :: %s' % file_path, to_console=True)
        now('Generated Path for File already exists!')

        if not cfg.config['OVER_WRITE']:
            now(
                'skipping :: Over writing of files is Disabled!',
                level=1,
                to_console=True
            )
            return file_path

        else:
            now('Existing file at %s removed!' % file_path)
            os.remove(file_path)

    # check if file path actually have a filename in it
    # file name if given e.g. file.html or file.asp else index.html
    if os.path.splitext(url_path(file_path))[1].find('.') == -1:
        file_comp = False
    else:
        file_comp = True

    if not file_comp:
        now(
            'error :: File path %s does not have a filename in it!' % file_path,
            level=3,
            to_console=True
        )
        return

    now('Generated valid path for File %s' % file_path)

    # if content of a file is to be filled through an url
    if url:
        now('Downloading file content from :: %s' % url)

        # fetch the url
        req = get(url)

        # extract request contents
        if req is None:
            now(
                'error :: Failed to load the file from url %s'
                % url,
                to_console=True,
                compressed=False,
                level=3
            )
            return

        # get the file type from request
        _mime_type = req.headers.get('Content-Type', 'text/plain')
        # store the content of the request
        content = req.content

    # open the file for writing
    with open(file_path, 'wb') as file_handle:

        if not url or _mime_type.split('/')[0] == 'text':
            file_handle.write(watermark(url or file_path))

        file_handle.write(content)
        file_handle.write(watermark(url or file_path))

    # last check if file was successfully
    if not os.path.isfile(file_path):
        raise RuntimeError(
            'error :: File writing at %s misfired!' % file_path,
            level=4,
            to_console=True
        )

    cfg.config['DOWNLOADED_FILES'].append(file_path)

    now(
        'success :: File %s written Successfully!' % file_path,
        to_console=True
    )

    # return the file path of the saved file
    return file_path


# ---------------------------------------------------------
# this func generates watermarks based on files
# with timestamps
# ---------------------------------------------------------
def watermark(file_path):
    # Watermarking method. This returns a string wrapped in comment type for specific file type.

    file_type = os.path.splitext(file_path)[1]

    if file_type == '.css' or file_type == '.js':
        comment_style = '/*!#*/'

    else:
        comment_style = '<!--!#-->'

    mark = """\n* AerWebCopy [version {}]\n* Copyright Aeroson Systems & Co.\n* File mirrored from {} \n* at {}\n""".format(
        cfg.config['version'],
        os.path.basename(file_path),
        datetime.datetime.utcnow()
    )

    # return a bytes converted whitespace stripped down comment
    # Compatibility issues due to byes type
    if py2:
        return bytes(comment_style.replace('#', mark))
    elif py3:
        return bytes(comment_style.replace('#', mark), 'utf-8')
    else:
        return comment_style.replace('#', mark)


# ----------------------------------------------------------------------
# toolkit func to log special `print` elements to external log file
# NOTE: this generates about minimum of 1000 lines of log per page or so,
# if you don't care about your python terminal filled with thousands of lines
# of log then set cfg.config['DEBUG']=True and see what's going on inside
# with ease
# -----------------------------------------------------------------------
def now(string, level=0, unbuffered=False, to_console=False, compressed=cfg.config['LOG_FILE_COMPRESSION']):
    """Writes any input string to external logfile

    :param string: any string which you want to write to log
    :param level: defines the priority of the string to end user
    : level 0: Regular event
    : level 1: Event Success
    : level 2: Check Passed
    : level 3: Check Failed
    : level 4: Critical Error
    :param unbuffered: whether to write the entry directly to log
    even when buffering is on
    :param to_console: also prints the string to python console
    :param compressed: reduces the string length to 80 characters
    """

    _event_level_strings = ["info", "warning", "error", "success"]

    if level == 4:
        _event_level = _event_level_strings[2]
    elif level == 1 or level == 2:
        _event_level = _event_level_strings[3]
    elif level == 3:
        _event_level = _event_level_strings[1]
    else:
        _event_level = _event_level_strings[0]

    # shorten the string
    if compressed:
        if len(string) > 80:
            string = '%s...%s' % (
                string[:40], string[len(string) - 36: len(string)])

    # if string is requested to be printed to console also
    if to_console:
        print(string)

    _caller = sys._getframe().f_back.f_code.co_name

    if _caller != '<module>':
        _caller = '<function {}>'.format(_caller)

    # standardisation of the input string
    if compressed:
        _formatted_string = "{} - [Level: {}] - {}".format(
            _caller, _event_level, string)
    else:
        _formatted_string = "[{}] - {} - [Level: {}] - {}".format(
            datetime.datetime.utcnow(), _caller, _event_level, string)

    # if _debug switch is true than this will write now() instances to console
    if cfg.config['DEBUG']:
        print(_formatted_string)

    # append the string to log array
    if cfg.config['LOG_BUFFERING'] and not unbuffered:
        cfg.config['LOG_BUFFER_ARRAY'].append(_formatted_string)
        return

    with open(cfg.config['LOG_FILE'], 'a+') as log_file:
        log_file.write(_formatted_string)
        log_file.write('\n\n')


# main func that runs and downloads html source code of page
def save_webpage(url):

    req = get(url)
    # check if request was successful
    if not req.ok:
        now('Server Responded with an error!', level=4, to_console=True)
        now('Error code: %s' % str(req.status_code), to_console=True)
        return

    # generate soup of the request
    soup = bs4.BeautifulSoup(req.content, 'html.parser')

    # file name if given e.g. file.html or file.asp else index.html
    if os.path.splitext(url_path(url))[1] == '.com':
        file_comp = 'index.html'

    elif os.path.splitext(url_path(url))[1].find('.') == -1:
        file_comp = 'index.html'

    elif url.endswith('/'):
        file_comp = 'index.html'

    else:
        file_comp = ''

    # we have make sure the url have an filename e.g. 'http://site.com' not
    # have a file name and we have to add 'index.html' to it
    url = urlparse.urljoin(url, file_comp).strip('/')

    now('built url :: %s' % url, to_console=True)

    # generate style map
    # NOTE: This takes initial file soup as arg not relative file named one
    # to increase the chances of finding the linked file
    generate_style_map(url, soup)

    # convert the css and js links to path relative to this file
    final_soup = generate_relative_paths(soup,
        os.path.join(
            cfg.config['MIRRORS_DIR'], compatible_path(url)
        )
    )

    # Compatibility issues to bytes func on py2 and py3
    if py2:
        content = bytes(str(final_soup))
    elif py3:
        content = bytes(str(final_soup), "utf-8")
    else:
        content = str(final_soup)

    # finally save this file
    # create a new file from soup
    saved_file = new_file(url, content=content)

    # parse any styles which are written in <style> tag of html file
    extract_css_urls(url_of_file=url, file_path=saved_file)


# store crawled url in a list
__crawled_urls__ = list()
__crawlable_urls__ = list()
# crawler to extract all the valid page links on the given page


# ----------------------------------------------------
# this fetches the first page and scans for links to
# other pages which are under the your given url
# ----------------------------------------------------
def crawl(url):

    now('Trying to start crawler on url %s' % url)

    # make a request to the page
    req = get(url)

    # something went wrong; exit
    if req is None:
        now('Crawler encountered an Error while requesting web page on url %s' %
            url, level=4)
        now('Crawler Exiting!', level=4)
        sys.exit(1)

    # page found and working
    # make a soup of it
    soup = bs4.BeautifulSoup(req.content, 'html.parser')

    # select all the links on page
    a_tags = soup.find_all('a', href=True)

    # store absolute url of them in a separate dict
    global __crawlable_urls__
    __crawlable_urls__ += set([
        urlparse.urljoin(url, i.get('href', ''))
        for i in a_tags
        if urlparse.urljoin(url, i.get('href', '')).startswith(url)
        ]
    )

    # save these pages
    if cfg.config['COPY_ALL']:
        for i in __crawlable_urls__:
            if i in __crawled_urls__:
                continue

            save_webpage(url=i)
            __crawled_urls__.append(i)

    else:
        if url not in __crawled_urls__:
            save_webpage(url)
            __crawled_urls__.append(url)

    # write all links found on the pages to indexed_links.txt
    with open(cfg.config['link_index_file'], 'w+') as index:

        now('Writing index of all found links!', level=1)

        index.truncate()
        index.write('\n'.join(__crawlable_urls__))

        now('Done! Index written.', level=1)
