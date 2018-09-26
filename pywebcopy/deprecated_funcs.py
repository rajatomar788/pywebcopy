# DEPRECATED #
# ----------------------------------------------------------------------
# toolkit func to log special `now` elements to external log file
# NOTE: this generates about minimum of 1000 lines of log per page or so,
# if you don't care about your python terminal filled with thousands of lines
# of log then set config['DEBUG']=True and see what's going on inside
# with ease
# -----------------------------------------------------------------------
def now(string, level=0, to_console=False):
    """ Writes any input string to external logfile

    :param string: any string which you want to write to log
    :param level: defines the priority of the string to end user
    : level 0: Debug Level Event
    : level 1: Event Success
    : level 2: Check Passed
    : level 3: Check Failed
    : level 4: Critical Error
    :param to_console: also prints the string to python console
    """
    warnings.warn("now() function is deprecated! Use pywebcopy.LOGGER instead!")
    if config['quiet']:
        return

    _event_level_strings = ["info", "error", "critical", "success"]

    if level == 4:
        _event_level = _event_level_strings[2]
    elif level == 1 or level == 2:
        _event_level = _event_level_strings[3]
    elif level == 3:
        _event_level = _event_level_strings[1]
    else:
        _event_level = _event_level_strings[0]

    _caller = sys._getframe().f_back.f_code.co_name

    if _caller != '<module>':
        _caller = '<function {}>'.format(_caller)

    # standardisation of the input string
    _formatted_string = "[{}] [{}] [{}] {}".format(
            datetime.utcnow(), _caller, _event_level, string)

    # if _debug switch is true than this will write now() instances to console
    # if string is requested to be printed to console also
    if config['DEBUG'] or to_console:
        print(_formatted_string)

    # if the location of log file is undefined; return
    if config['LOG_FILE'] is None:
        return

    with open(config['LOG_FILE'], 'a') as log_file:
        log_file.write(_formatted_string)
        log_file.write('\n\n')


def _save_file(link_obj, attr, base_url=None, base_path=None):
    """ Saves linked file and Replace the files location in document with file saved on disk """

    # get the 'href' attribute of html element
    _url = link_obj.get(attr, '')

    # create a absolute url
    abs_url = utils.join_urls(config['project_url'], _url)

    # check if the link is just domain or empty
    if base_url and utils.url_path(abs_url) in ('/', '', '\\'):
        return '', ''

    # if the downloading is not requested
    # TODO : Change for anchor tags
    if True:

        try:
            # if a single page is being downloaded then the links on the page
            # should all be absolute so that when we click on them they do not throw and
            # file not found error
            if not config['copy_all']:
                LOGGER.debug('Replacing url :: %s' % _url)
                link_obj[attr] = abs_url
                LOGGER.debug('Replaced with url %s' % link_obj[attr])
                return abs_url, ''

            # create a absolute path from the url
            path = generate_path_for(_url, base_url, False, None, False)
            # repace html attribute value with new relative url
            link_obj[attr] = pathname2url(utils.relate(path, base_path))

            return '', ''

        except:
            return '', ''
    else:
        try:
            # create directory for path
            path = generate_path_for(_url, base_url, False, None, True)
        except Exception as e:
            LOGGER.exception(e.message)
            LOGGER.debug('Failed to create path for file %s' % _url)
            return '', ''

    # save the file
    try:
        _saved_file_path = core.new_file(path, content_url=utils.join_urls(base_url, _url))
    except:
        return '', ''

    # generate a relative url
    final_url = pathname2url(utils.relate(_saved_file_path, base_path))

    # finally replace the link in file_soup object
    link_obj[attr] = final_url

    LOGGER.info('Replaced url %s with :: %s' % (_url, final_url))

    # remove 'crossorigin' or similar attributes so that the browser
    # loads the css or scripts without CORS restriction
    if link_obj.get('crossorigin') is not None:
        del link_obj['crossorigin']
    if link_obj.get('integrity') is not None:
        del link_obj['integrity']
    if link_obj.get('srcset') is not None:
        del link_obj['srcset']

    return utils.join_urls(base_url, _url), _saved_file_path


def generate_path_for(url, base_url=None, filename_check=False, default_filename='file', create_path=True):
    """ Creates a valid file path from urls.

    :param url: url from path to be generated
    :param base_url: url to be joined to relative 'url'
    :param filename_check: if a filename is required to be generated in path
    :param default_filename: filename to be added to path if filename not present
    :param create_path: to create the path on disk or not
    :returns: path generated
    """

    LOGGER.info('Generating path for %s url.' % url)

    # create absolute url if given url is absolute or not
    if base_url:
        url = utils.join_urls(base_url, url)
    else:
        url = utils.join_urls(config['url'], url)

    # if filename is required in generated path
    if filename_check:
        if os.path.splitext(url)[-1].find('.') == -1 or \
                os.path.splitext(url)[-1] == utils.hostname(url).split('.')[-1]:
            if default_filename is None:
                raise InvalidPathError("Default Filename is not valid %s" % url)
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
    _path = config['filename_validation_pattern'].sub('', _path)

    if not _path:
        return _path

    # return the newly made path
    path = os.path.join(config['project_folder'], os.path.dirname(_path))

    if create_path:
        # make this path if not exists
        utils.make_path(path)

    # final path with file name
    path = utils.join_paths(path, file_comp)

    LOGGER.info('Generated Path %s' % path)

    return path
