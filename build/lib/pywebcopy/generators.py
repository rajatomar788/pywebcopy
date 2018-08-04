# -*- coding: utf-8 -*-

"""
aerwebcopy.generators
~~~~~~~~~~~~~~~~~~~~~

Data & patterns generators powering aerwebcopy.
"""


import os
import re
from utils import *
import core
import config

if core.py2:
    from urllib import pathname2url
elif core.py3:
    from urllib.request import pathname2url


__all__ = [
    "generate_relative_paths", "generate_path_for", "generate_style_map", "extract_css_urls"
]


# toolkit func to create dirs and return dir for storage of file
def generate_path_for(url, create_path=True):

    # removes from url http scheme or ports or non valid characters
    url = compatible_path(url)

    if not file_path_is_valid(url):
        core.now('File Name %s is not valid!' % url, level=4)
        raise TypeError('File Name %s is not valid!' % url)

    # here parsing of the url is done to get a valid
    # filename or dir name to create
    # domain name is eg. www.google.com
    file_comp = get_filename(url)

    # return the newly made path
    correct_path = os.path.abspath(
        os.path.join(
            config.config['MIRRORS_DIR'], url.replace(file_comp, '').strip('/')
        )
    )

    if create_path:
        # make this path if not exists
        make_path(correct_path)

    core.now(
        'Path :: %s' % os.path.abspath(
            os.path.join(correct_path, file_comp)
        )
    )

    # return the full path made for file with filename
    return os.path.abspath(os.path.join(correct_path, file_comp))


# toolkit func to download and replace urls used in css
def extract_css_urls(url_of_file, file_content=None, file_path=None):
    """
    Extracts url() links in css and saves and
    replaces them in file
    all the linked file url() will be saved and file path
    would be replaced accordingly

    :param url_of_file: basic url of the file to match the urls for relating paths
    :param file_content: string formatted content of the file to be searched
    :param file_path: either url_of_file or file_path of the file on system drive
    :return: None
    """

    # if system drive path of the file is given
    if file_path:

        # file can be corrupted to open
        try:
            # read the file
            core.now('Reading Existing file at %s' % file_path)
            file_content = open(file_path, 'rb').read()
            core.now('Finding CSS urls in file %s' % file_path)

        except IOError:
            core.now(
                'Failed to open file %s for CSS urls search' % file_path,
                level=4
            )

    # convert the file_content to string format
    file_content = str(file_content)

    # find all css urls
    _urls = re.findall(r'''url\(['|"](.*?)['|"]\)''', file_content, flags=re.UNICODE)

    core.now('CSS url search completed Successfully!')

    # if links are not found
    if len(_urls) == 0:
        core.now('No CSS linked files are found!')
        return

    # links are found, now extract and replace them
    core.now('%d CSS linked files are found!' % len(_urls))

    core.now('Extracting linked css files!')

    for _url in _urls:

        linked_file_url = join_urls(url_of_file, _url)

        # make sure the url is valid url
        if not file_path_is_valid(compatible_path(linked_file_url)):

            core.now(
                'Linked file %s is not valid!' % linked_file_url,
                level=3
            )
            continue

        # save these files
        core.new_file(linked_file_url, content=None, url=linked_file_url)

        # generate a relative path for this downloaded file
        _rel_url = pathname2url(relate(
            os.path.abspath(join_paths(config.config['mirrors_dir'], compatible_path(linked_file_url))),
            os.path.abspath(file_path)
        ))
        core.now('Replacing linked file path %s by %s' % (_url, _rel_url))
        # replace the location of the downloaded file on the original file
        file_content = file_content.replace(_url, _rel_url)

    # rewrite the original file to contain the newly downloaded file links
    with open(file_path, 'w+') as orig_file:
        orig_file.truncate()
        orig_file.write(file_content)
        orig_file.close()


# toolkit func generate a list of stylesheets and js files used on the page
def generate_style_map(file_url, file_soup):

    # save them
    def fetch(asset_url):
        # return the saved file path if needed
        return core.new_file(
            join_urls(config.config['URL'], asset_url),
            content=None, 
            url=asset_url
        )

    # if stylesheet download is allowed
    if config.config['LOAD_CSS']:

        stylesheets = [
            join_urls(file_url, i.get('href', ''))
            for i in file_soup.find_all('link', href=True)
        ]

        for sheet in stylesheets:
            saved_file_path = fetch(sheet)

            # fetch also the urls used inside css
            core.now('Sending %s file for CSS urls search!' % saved_file_path)

            extract_css_urls(
                url_of_file=sheet, 
                file_path=saved_file_path
            )

    # if js download is allowed
    if config.config['LOAD_JAVASCRIPT']:

        js = [
            join_urls(file_url, i.get('src', ''))
            for i in file_soup.find_all('script', src=True)
        ]

        for x in js:
            fetch(x)

    # if image download is allowed
    if config.config['LOAD_IMAGES']:

        images = [
            join_urls(file_url, i.get('src', ''))
            for i in file_soup.find_all('img', src=True)
        ]

        for image in images:
            fetch(image)


# toolkit func to generate relative paths for css and js files
def generate_relative_paths(file_soup, file_path):
    """
    Generates file soup with links to files and pages converted from
    absolute to relative for preventing page not found error while
    browsing offline

    :param file_soup: beautiful_soup object of the file to be modified
    :param file_path: current file path of the file on system drive
    :return: beautiful_soup objects with urls and css, js links converted
    to relative path
    """

    def replace(link_obj, attr):

        # return if the link is a special content holder
        if link_obj.get(attr, '#').startswith(('#', 'base64', 'java', '<svg', '<xml')):
            return

        # check if link is not some placeholder
        if not file_path_is_valid(compatible_path(link_obj.get(attr, ''))):
            return

        # create a compatible path without http url or port names etc.
        initial_url = compatible_path(
            join_urls(config.config['URL'], link_obj.get(attr, ''))
        )

        # concatenate this path with the base dir of operation
        initial_url = os.path.abspath(
            os.path.join(config.config['MIRRORS_DIR'], initial_url)
        )

        core.now('Original url :: %s' % initial_url)

        # generate a relative url
        final_url = pathname2url(relate(initial_url, file_path))

        core.now('Final url :: %s' % final_url)

        # finally replace the link in file_soup object
        link_obj[attr] = final_url

        # remove 'crossorigin' or similar attributes so that the browser
        # loads the css or scripts without CORS restriction
        if link_obj.get('crossorigin') is not None:
            del link_obj['crossorigin']
        if link_obj.get('integrity') is not None:
            del link_obj['integrity']

        return final_url

    # replace all the css links
    for i in file_soup.find_all('link', href=True):
        replace(i, 'href')
    # place it before closing ']' to verify css presence
    # if i.get('href', ' ').endswith('.css')
    
    core.now('CSS links replaced Successfully!')

    # replace all js links
    for i in file_soup.find_all('script', src=True):
        replace(i, 'src')
    # if i.get('src', ' ').endswith('.js')
    
    core.now('JS links replaced Successfully!')

    # replace all img src links
    for i in file_soup.find_all('img', src=True):
        # checks if the img is not a base64 encoded data
        if not i.get('src', '').startswith('data'):
            replace(i, 'src')
    
    core.now('Image links replaced Successfully!')

    # replace all the generic anchor tags of the page
    for i in file_soup.find_all('a', href=True):
        replace(i, 'href')

    core.now('Page links replaced Successfully!')

    # return the modified file soup
    return file_soup
