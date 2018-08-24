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
import zipfile
import threading
import logging
import os
import bs4
import requests

py2 = True if sys.version_info.major == 2 else False
py3 = True if sys.version_info.major == 3 else False

if py2:
    import urlparse
elif py3:
    from urllib import parse as urlparse
else:
    raise ImportError("Error while importing Modules!")

from pywebcopy.exceptions import AccessError, InvalidUrl, ConnectError
from pywebcopy import config as cfg

SESSION = requests.Session()
LOGGER = logging.getLogger("pyebcopy")
LOGGER.setLevel(logging.DEBUG)

CLOGGER = logging.StreamHandler()
CLOGGER.setLevel(logging.ERROR)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
formatter.datefmt = "%d-%b-%Y %H:%M:%S"
CLOGGER.setFormatter(formatter)
LOGGER.addHandler(CLOGGER)


def save_webpage(url, mirrors_dir, reset_config=True, **kwargs):
    """ Starts crawler, archives and writes logs etc. """

    cfg.setup_config(url, mirrors_dir, **kwargs)

    # Add a log file writer to Logger
    FLOGGER = logging.FileHandler(cfg.config['log_file'])
    FLOGGER.setLevel(logging.DEBUG)
    FLOGGER.setFormatter(formatter)
    LOGGER.addHandler(FLOGGER)

    # save the page
    _crawl(cfg.config['URL'])

    # Everything is done! Now Clean up and write logs.
    wrap_up()

    if reset_config:
        # reset the config so that it does not mess up
        cfg.reset_config()

    # ALL DONE
    print("All Done!")


def wrap_up():
    """ Print Useful information about completed project to python console. """

    now(
        "Downloaded Content :: %s KB's" % str(
            cfg.config['DOWNLOAD_SIZE'] // 1024),
        to_console=True
    )
    now(
        'Downloaded Files :: \n%s' % '\n'.join(
            cfg.config['DOWNLOADED_FILES'])
    )


    if cfg.config['MAKE_ARCHIVE']:

        # NOTE: Old Method, a one-liner
        '''_archive = shutil.make_archive(
            os.path.abspath(cfg.config['MIRRORS_DIR']), 'zip',
            root_dir=os.path.abspath(cfg.config['MIRRORS_DIR'])
        )'''

        # NOTE: new method, less error prone
        # make zip archive of all the files and not the empty folders
        archive = zipfile.ZipFile(
            os.path.abspath(cfg.config['MIRRORS_DIR']) +
            '.zip', 'w', zipfile.ZIP_DEFLATED
        )

        for foldername, _, filenames in os.walk(cfg.config['MIRRORS_DIR']):
            # os.walk returns 3-tuples of foldername, subfoldername,
            # filenames

            # we add only files to the archive
            for filename in filenames:

                try:
                    _temp_filename = os.path.join(foldername, filename)
                    archive.write(
                        _temp_filename, _temp_filename[len(cfg.config['mirrors_dir']):])

                except Exception as e:
                    now("File %s generated %s error while adding to archive." % (
                        filename, e.message), level=3)

        archive.close()

        now('Saved the Project as ZIP archive at %s' % (cfg.config['MIRRORS_DIR'] + '.zip'),
            to_console=True
            )

    # delete the temp folder after making archive
    if cfg.config['CLEAN_UP']:
        # clean up the mirrors dir

        print('Cleaning up %s' % cfg.config['MIRRORS_DIR'])

        shutil.rmtree(cfg.config['MIRRORS_DIR'])


def _can_access(user_agent, url):
    """ Determines if user-agent is allowed to access url. """

    if not cfg.config['robots'] or cfg.config['robots'].is_dummy:
        return True

    # check if website allows bot access
    if not cfg.config['ROBOTS'].can_fetch(user_agent, url) and not cfg.config['BYPASS_ROBOTS']:

        now(
            "error :: Website doesn't allow access to the url %s" % url,
            to_console=True,
            level=3
        )
        return False

    elif not cfg.config['ROBOTS'].can_fetch(user_agent, url) and cfg.config['BYPASS_ROBOTS']:
        now(
            'forced :: Accessing restricted website part %s' % url,
            to_console=True,
            level=2
        )
        return True

    else:
        return True


# ---------------------------------------------------------
# toolkit func to make requests using custom configs
# it returns request content if request was successful
# None otherwise.
# ---------------------------------------------------------
def get(url):
    """ fetches web page from internet using `requests`.

    :param url: the url of the page or file to be fetched
    :returns: fetched page
    """

    if not _can_access("*", url):
        raise AccessError("Access to %s not allowed by site." % url)

    headers = {
        "Accept-Language": "en-US,en;q=0.5",
        'User-Agent': cfg.config['USER_AGENT']
    }

    # this returns a request object fetched through the module
    try:

        # make request to page
        req = SESSION.get(url, headers=headers)

        # log downloaded file size
        cfg.config['DOWNLOAD_SIZE'] += int(
            req.headers.get('content-length', 0))

        return req

    except Exception as e:
        now(
            'error :: Internet Connection not Found!',
            level=4,
            to_console=True
        )
        return




# -----------------------------------------------------------
# toolkit func to generate a file with filename and data
# it checks various expects before creating a file
# but it is as easy as `new_file('pathtofile', 'filecontent')`
# -----------------------------------------------------------
def new_file(download_loc, content_url=None, content=None):
    """ Downloads any file to the disk.

    :param download_loc: path where to save the file

    :param content: contents or binary data of the file
    :OR:
    :param content_url: download the file from url

    :returns: location of downloaded file on disk
    """

    if not download_loc or not (content or content_url):
        return download_loc

    now('Saving file at %s path' % download_loc)

    # if content of a file is to be filled through an content_url
    if content_url:
        now('Downloading file content from :: %s' % content_url)

        try:
            # fetch the content_url
            req = get(content_url)

            if not req or not req.ok:
                return download_loc

            # store the content of the request
            content = req.content

        except Exception as e:
            now(
                'error :: Failed to load the file from content_url %s due to error %s'
                % (content_url, e.message),
                to_console=True,
                compressed=False,
                level=4
            )
            return download_loc

    # if file of this type is allowed to be saved
    if not os.path.splitext(download_loc)[-1].lower() in cfg.config['ALLOWED_FILE_EXT']:
        now(
            'error :: file of type %s is not allowed!'
            % str(os.path.splitext(download_loc)[-1]),
            level=3,
            to_console=True
        )
        return download_loc

    # if newly created download_loc already a file
    if os.path.exists(download_loc):

        now('exists :: %s' % download_loc, to_console=True)

        if not cfg.config['OVER_WRITE']:

            now('skipping :: Over writing of files is Disabled!', 1, to_console=True)

            return download_loc

        else:
            now('Existing file at %s removed!' % download_loc)
            os.remove(download_loc)

    try:
        # Write the File
        with open(download_loc, 'wb') as f:

            _water_mark = _watermark(content_url or download_loc)
            f.write(_water_mark)
            f.write(content)
            f.write(_water_mark)
    except Exception as e:
        now("Exception occured during writing file %s exception %s" %(download_loc, e.message), level=4)
        return download_loc

    cfg.config['downloaded_files'].append(download_loc)

    now('success :: File %s written Successfully!' % download_loc, to_console=True)

    # return the file path of the saved file
    return download_loc


# ---------------------------------------------------------
# this func generates watermarks based on files
# with timestamps
# ---------------------------------------------------------
def _watermark(file_path):
    # Watermarking method. This returns a string wrapped in comment type for specific file type.

    file_type = os.path.splitext(file_path)[-1]

    if file_type in ['.html', '.htm', '.xhtml', '.aspx', '.asp', '.php']:
        comment_style = '<!--!#-->'
    elif file_type in ['.css', '.js', '.xml']:
        comment_style = '/*!#*/'
    else:
        return b''

    mark = """
    * AerWebCopy [version {}]
    * Copyright Aeroson Systems & Co.
    * File mirrored from {}
    * at {}
    """.format(
                cfg.config['version'],
                os.path.basename(file_path),
                datetime.datetime.utcnow()
            )

    if py3:
        return bytes(comment_style.replace('#', mark), 'utf-8')
    else:
        return bytes(comment_style.replace('#', mark))


# ----------------------------------------------------------------------
# toolkit func to log special `now` elements to external log file
# NOTE: this generates about minimum of 1000 lines of log per page or so,
# if you don't care about your python terminal filled with thousands of lines
# of log then set cfg.config['DEBUG']=True and see what's going on inside
# with ease
# -----------------------------------------------------------------------

def now(string, level=0, unbuffered=False, to_console=False, compressed=cfg.config['LOG_FILE_COMPRESSION']):
    """ Writes any input string to external logfile

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

    # shorten the string
    if compressed:
        if len(string) > 80:
            string = '%s...%s' % (
                string[:40], string[len(string) - 36: len(string)])

    _caller = sys._getframe().f_back.f_code.co_name

    if _caller != '<module>':
        _caller = '<function {}>'.format(_caller)

    # standardisation of the input string
    _formatted_string = " [{}] {}".format(
        _caller, string)


    # if _debug switch is true than this will write now() instances to console
    # if string is requested to be printed to console also
    if cfg.config['DEBUG'] or to_console and not cfg.config['quiet']:
        print(_formatted_string)

    # if the location of log file is undefined; return
    if not cfg.config['LOG_FILE']:
        return
    LOGGER.log(level * 10,_formatted_string)


# main func that runs and downloads html source code of page
def _save_webpage(url):
    """ Saves any web page to the disk.

    NOTE: This functions assumes that all the configuration is done, 
    so if you try to run this with only 'url' param, it is most likely
    that it will generate an exception.
    """

    req = get(url)

    # check if request was successful
    if not req or not req.ok:
        now('Server Responded with an error!', level=4, to_console=True)
        now('Error code: %s' % str(req.status_code), to_console=True)
        return req.status_code

    # generate soup of the request
    soup = bs4.BeautifulSoup(req.content, cfg.config['parser'])

    from pywebcopy import generators as gens

    # create a path where to download this page
    download_path = gens.generate_path_for(url, filename_check=True, default_filename='index.html')

    # store the file name generated for the url
    file_comp = os.path.split(download_path)[-1]

    # the url may not have an filename e.g. 'http://site.com' not
    # have a file name and we have to add file name to it
    url = urlparse.urljoin(url, file_comp).strip('/')

    now('built url :: %s' % url, to_console=True)

    # generate style map
    # NOTE: This takes initial file soup as arg not relative file named one
    # to increase the chances of finding the linked file

    final_soup = gens.generate_style_map(url, download_path, soup)

    # Compatibility issues to bytes func on py2 and py3
    if py2:
        content = bytes(str(final_soup))
    else:
        content = bytes(str(final_soup), "utf-8")

    # finally save this file
    # create a new file from soup
    saved_file = new_file(download_path, content=content)

    # parse any styles which are written in <style> tag of html file
    gens.extract_css_urls(url_of_file=url, file_path=saved_file)


# ----------------------------------------------------
# this fetches the first page and scans for links to
# other pages which are under your given url
# ----------------------------------------------------
crawled_urls = list()
crawlable_urls = list()


def _crawl(url, level=0, max_level=2):
    """ Scans pages for links to other pages to save in COPY_ALL mode.
    """

    # if single webpage is requested
    if not cfg.config['copy_all']:
        _save_webpage(url)
        crawled_urls.append(url)

        return

    # if max deep level is reached
    if level == max_level:
        return

    # crawler to extract all the valid page links on the given page
    now('Trying to start crawler on url %s' % url, to_console=True)

    # make a request to the page
    req = get(url)

    # something went wrong; exit
    if not req.ok:
        now('Crawler encountered an Error while requesting web page on url %s' %
            url, level=4, to_console=True)
        now('Crawler Exiting!', level=4, to_console=True)
        sys.exit(1)

    # page found and working
    # make a soup of it
    soup = bs4.BeautifulSoup(req.content, cfg.config['parser'])

    # select all the links on page
    a_tags = soup.find_all('a', href=True)

    # store absolute url of them
    global crawlable_urls
    crawlable_urls += set([urlparse.urljoin(url, i.get('href', ''))
                           for i in a_tags if urlparse.urljoin(url, i.get('href', '')).startswith(url)])

    # every url found will be checked and sent to be saved through the 
    # save_webpage method
    for url in crawlable_urls:

        # if url is already saved
        if url in crawled_urls:
            # go to the next url
            continue

        # otherwise save this url and add this to saved list
        _save_webpage(url)
        crawled_urls.append(url)

        # send this url again for url searching
        _crawl(url, level=(level + 1))

    now("Crawled URL list : ")
    now('\n'.join(crawlable_urls))
