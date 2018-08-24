# -*- coding: utf-8 -*-

from __future__ import print_function

"""
aerwebcopy.generators
~~~~~~~~~~~~~~~~~~~~~

Data & patterns generators powering aerwebcopy.
"""

import os
import re

from pywebcopy import exceptions
from pywebcopy import config
from pywebcopy import utils
from pywebcopy import core

if core.py2:
    from urllib import pathname2url, url2pathname
elif core.py3:
    from urllib.request import pathname2url, url2pathname
else:
    raise ImportError("Error while importing Modules!")


@utils.trace
def generate_path_for(url, base_url=None, filename_check=False, default_filename=None, create_path=True):
    """ Creates a valid file path from urls.

    :param url: url from path to be generated
    :param base_url: url to be joined to relative 'url'
    :param filename_check: if a filename is required to be generated in path
    :param default_filename: filename to be added to path if filename not present
    :param create_path: to create the path on disk or not
    :returns: path generated
    """

    core.now('Generating path for %s url.' % url)

    # create absolute url if given url is absolute or not
    if base_url:
        url = utils.join_urls(base_url, url)
    else:
        url = utils.join_urls(config.config['url'], url)

    # if filename is required in generated path
    if filename_check:
        if os.path.splitext(url)[-1].find('.') == -1 or \
                os.path.splitext(url)[-1] == utils.hostname(url).split('.')[-1]:
            if default_filename is None:
                raise exceptions.InvalidFilename("Default Filename is not valid.")
            else:
                file_comp = default_filename
        else:
            file_comp = utils.get_filename(url)
        # join file name to url
        url = utils.join_urls(url, file_comp)

    else:
        file_comp = utils.get_filename(url)

    # removes from url http scheme or ports or non valid characters
    _path = url2pathname(utils.compatible_path(url))

    # remove any invalid chars
    _path = config.config['filename_validation_pattern'].sub('', _path)

    if not _path:
        return _path

    # return the newly made path
    try:
        path = os.path.abspath(
            os.path.join(
                config.config['MIRRORS_DIR'], os.path.dirname(_path)
            )

        )
    except:
        return _path

    if create_path:
        # make this path if not exists
        utils.make_path(path)

    # final path with file name
    path = utils.join_paths(path, file_comp)

    core.now('Path Generated :: %s' % path)

    return path


def extract_css_urls(url_of_file, file_path):
    """
    Extracts url() links in css and saves and
    replaces them in file
    all the linked file url() will be saved and file path
    would be replaced accordingly

    :param url_of_file: basic url of the file to match the urls for relating paths
    :param file_path: either url_of_file or file_path of the file on system drive
    :return: None
    """

    if file_path is None:
        return

    # file can be corrupted to open
    try:
        # read the file
        core.now('Reading Existing file at %s' % file_path)
        file_content = open(file_path, 'rb').read()

    except IOError:
        core.now(
            'Failed to open file %s for CSS urls search' % file_path,
            level=4
        )
        return
    except UnicodeDecodeError:
        core.now(
            'Failed to open file %s for CSS urls search' % file_path,
            level=4
        )
        return

    core.now('Finding CSS urls in file %s' % file_path)
    # find all css urls
    _urls = re.findall(b'url\\((.*?)\\)', file_content)
    # the _urls also have those with double mix-match quotes
    _urls = [x.strip(b'"').strip(b"'") for x in _urls]

    core.now('CSS url search completed Successfully!')

    # if links are not found
    if len(_urls) == 0:
        core.now('No CSS linked files are found!')
        return

    # links are found, now extract and _save_linked_file them
    core.now('%d CSS linked files are found!' % len(_urls))

    core.now('Extracting linked css files!')

    for _url in _urls:

        # convert bytes url to string
        try:
            _str_url = _url.decode('utf-8')
        except UnicodeDecodeError:
            continue

        # url can be encoded content
        if 'base64' in _str_url:
            continue

        try:
            # generate a dummy path based on url
            _path = generate_path_for(_str_url, url_of_file)
        except:
            continue

        # save this file
        core.new_file(_path, content=None, content_url=utils.join_urls(url_of_file, _str_url))

        # generate a relative path for this downloaded file
        _rel_url = pathname2url(utils.relate(
            _path, os.path.abspath(file_path)
        ))
        core.now('Replacing linked file path %s by %s' % (_str_url, _rel_url))

        # _save_linked_file the location of the downloaded file on the original file
        if core.py2:
            _rel_url = bytes(_rel_url)
            _url = bytes(_url)
            file_content = re.sub(_url, _rel_url, file_content)
        else:
            # reconvert to bytes
            _rel_url = bytes(_rel_url, 'utf-8')

            file_content = re.sub(_url, _rel_url, file_content)

    # rewrite the original file to contain the newly downloaded file links
    with open(file_path, 'wb') as orig_file:
        orig_file.truncate()
        orig_file.write(file_content)


@utils.trace
def _save_linked_file(link_obj, attr, base_url=None, base_path=None, download_file=True):
    """ Saves linked file and Replace the files location in document with file saved on disk """

    # get the 'href' attribute of html element
    _url = link_obj.get(attr, '')

    # create a absolute url
    abs_url = utils.join_urls(config.config['url'], _url)

    # check if the link is just domain or empty
    if base_url and utils.url_path(abs_url) in ('/', '', '\\'):
        return '', ''

    # if the downloading is not requested
    if not download_file:

        try:
            # if a single page is being downloaded then the links on the page
            # should all be absolute so that when we click on them they do not throw and
            # file not found error
            if not config.config['copy_all']:
                core.now('Replacing url :: %s' % _url)
                link_obj[attr] = abs_url
                core.now('Replaced with url %s' % link_obj[attr])
                return abs_url, ''

            # create a absolute path from the url
            path = generate_path_for(_url, base_url, False, None, False)
            # _save_linked_file html attribute with relative url
            link_obj[attr] = pathname2url(utils.relate(path, base_path))

            return '', ''

        except:
            return '', ''
    else:
        try:
            # create directory for path
            path = generate_path_for(_url, base_url, False, None, True)
        except:
            core.now('error :: Path creation for file %s failed' % _url)
            return '', ''

    # save the file
    try:
        _saved_file_path = core.new_file(path, content_url=utils.join_urls(base_url, _url))
    except:
        return '', ''

    core.now('Replacing url :: %s' % _url)

    # generate a relative url
    final_url = pathname2url(utils.relate(_saved_file_path, base_path))

    # finally _save_linked_file the link in file_soup object
    link_obj[attr] = final_url

    core.now('Replaced url with :: %s' % link_obj[attr])

    # remove 'crossorigin' or similar attributes so that the browser
    # loads the css or scripts without CORS restriction
    if link_obj.get('crossorigin') is not None:
        del link_obj['crossorigin']
    if link_obj.get('integrity') is not None:
        del link_obj['integrity']
    if link_obj.get('srcset') is not None:
        del link_obj['srcset']

    return utils.join_urls(base_url, _url), _saved_file_path


def generate_style_map(file_url, file_path, file_soup):
    """ Saves css, js and img to disk and replaces their location on 
    page soup.

    Generates file soup with links to files and pages converted from
    absolute to relative for preventing file not found error while
    browsing offline

    :param file_url: absolute url of the web page e.g. with 'http' & filename or 'index.html'
    :param file_path: current file path of the file on system drive
    :param file_soup: beautiful_soup object of the file to be modified
    :return: beautiful_soup object with urls and css, js saved and their links 
    converted to relative path
 
    """

    # if stylesheet download is allowed
    if config.config['LOAD_CSS']:

        # _save_linked_file all the css links
        for link_obj in file_soup.find_all('link', href=True):

            # fetch also the urls used inside css
            url, saved_file_path = _save_linked_file(link_obj, 'href', file_url, file_path)

            if saved_file_path is None or url is None:
                continue

            core.now('Sending %s file for CSS urls search!' % saved_file_path)

            extract_css_urls(
                url_of_file=url,
                file_path=saved_file_path
            )

    # if js download is allowed
    if config.config['LOAD_JAVASCRIPT']:
        # get all the js src
        _js = file_soup.find_all('script', src=True)

        core.now("%d Js Linked files found!" % len(_js))
        for i in _js:
            _save_linked_file(i, 'src', file_url, file_path)

    # if image download is allowed
    if config.config['LOAD_IMAGES']:
        _img = file_soup.find_all('img', src=True)
        core.now("%d linked images found!" % len(_img))

        for i in _img:
            _save_linked_file(i, 'src', file_url, file_path)

    # _save_linked_file all the generic anchor tags of the page
    for i in file_soup.find_all('a', href=True):
        _save_linked_file(i, 'href', file_url, file_path, download_file=False)

    # return the modified file soup
    return file_soup
