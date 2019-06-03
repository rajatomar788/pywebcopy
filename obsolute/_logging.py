# encoding: utf-8

"""
HTML logger inspired by the Horde3D logger.

Usage:

- HTMLLogger instance with name, level, title, mode, version etc.
- call log, debug, info etc. on the instance
"""
from __future__ import absolute_import
import time
import logging

from . import __version__


#: HTML header starts the document
_HTML_DOC_START = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>%(title)s</title>
<style type="text/css">
body, html {
background: #000000;
font-family: Arial;
font-size: 16px;
color: #C0C0C0;
}
h1 {
color : #FFFFFF;
border-bottom : 1px dotted #888888;
}
pre {
font-family : arial;
margin : 0;
}
table {
border-collapse: collapse;
width: 100%%;
}
th, td {
text-align: left;
padding: 8px;
}

th {
background-color: #4CAF50;
color: white;
}
.box {
border : 1px dotted #818286;
padding : 5px;
margin: 5px;
background-color : #292929;
}
.err {
color: #EE1100;
font-weight: bold
}
.warn {
color: #FFCC00;
font-weight: bold
}
.info {
color: #C0C0C0;
}
.debug {
color: #CCA0A0;
}
.success {
color: #4CAF50;
}
</style>
</head>

<body>
<h1>%(title)s <small>%(version)s</small></h1>
<div class="box">
<table>
<tr>
    <th>Level</th>
    <th>Time</th>
    <th>Message</th>
</tr>
"""

_HTML_DOC_END = """</table>
</div>
<footer>
Pywebcopy Logger
</footer>
</body>
</html>
"""

_MSG_FMT = """
<tr class="%(class)s">
<td >%(level)s</td>
<td >%(time)s</td>
<td ><pre>%(msg)s</pre></td>
<tr>
"""


class HTMLFileHandler(logging.FileHandler):
    """
    File handler specialised to write the start of doc as html and to close it
    properly.
    """

    def __init__(self, title, version, *args):
        super(HTMLFileHandler, self).__init__(*args)
        self.stream.write(_HTML_DOC_START % {"title": title, "version": version})

    def close(self):
        # finish document
        self.stream.write(_HTML_DOC_END)
        super(HTMLFileHandler, self).close()


class HTMLFormatter(logging.Formatter):
    """
    Formats each record in html
    """
    css_classes = {'WARNING' : 'warn',
                   'INFO'    : 'info',
                   'DEBUG'   : 'debug',
                   'CRITICAL': 'err',
                   'ERROR'   : 'err',
                   'SUCCESS' : 'success',
                   'ACTION'  : 'action',
                   }

    datefmt = "%d-%b-%Y %H:%M:%S"

    def __init__(self):
        super(HTMLFormatter, self).__init__()

    def format(self, record):
        """Formats a record into a html string representation."""

        class_name = self.css_classes.get(record.levelname, 'info')

        t = self.formatTime(record, self.datefmt)

        # handle '<' and '>' (typically when logging %r)
        msg = record.getMessage()
        msg = msg.replace("<", "&#60")
        msg = msg.replace(">", "&#62")

        return _MSG_FMT % {"class": class_name, 'level': record.levelname, "time": t, "msg": msg}


# ============================================================
#   Global logger object setup
# ============================================================


LOGGER = logging.getLogger("pywebcopy")
LOGGER.__doc__ = """Global Logger object for logging purpose use in modules."""
LOGGER.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s.%(module)s"
                                 ".%(funcName)s:%(lineno)d - %(message)s")

# logFormatter = logging.Formatter("%(levelname)s - %(message)s")

logFormatter.datefmt = "%d-%b-%Y %H:%M:%S"
logFormatter.__doc__ = """Formatter to be used in logger object for formatting log entries."""

"""Add custom logging levels for ease of information flow."""
successLevelNum = 25
actionLevelNum = 21


def success(self, message, *args, **kws):
    self._log(successLevelNum, message, args, **kws)


def action(self, message, *args, **kws):
    self._log(actionLevelNum, message, args, **kws)


logging.addLevelName(successLevelNum, "SUCCESS")
logging.Logger.success = success
logging.addLevelName(actionLevelNum, "ACTION")
logging.Logger.action = action


def new_html_logger(title="PywebCopy Log", version=__version__, filename='log.html', mode='w'):
    """Creates a new html file logging handler for use in logger.

    :rtype: HTMLFileHandler
    :return: new HTLMFileHandler object
    """

    # Setup a html formatter for use
    html_formatter = HTMLFormatter()

    # Create a html file stream handler
    html_file_handler = HTMLFileHandler(title, version, filename, mode)
    html_file_handler.setFormatter(html_formatter)

    return html_file_handler


def new_console_logger(level=logging.WARNING):
    """Creates a new console logging handler for use in logger.

    :rtype: logging.StreamHandler
    :return: new logging.StreamHandler object
    """
    c_logger = logging.StreamHandler()
    c_logger.setLevel(level)
    c_logger.setFormatter(logging.Formatter("%(levelname)-8s - %(message)s"))
    return c_logger


def new_file_logger(file_path, mode):
    """Creates a new file logging handler for use in logger.

    :param file_path: where the file will be created
    :param mode: mode in which the file will be opened. See loggings module
    :rtype: logging.FileHanlder
    :return: new logging.FileHandler object
    """
    f_logger = logging.FileHandler(file_path, mode)
    f_logger.setLevel(logging.DEBUG)
    f_logger.setFormatter(logFormatter)
    return f_logger


# Example of usage
if __name__ == "__main__":
    LOGGER.debug("A debug message")
    LOGGER.info("An information message")
    LOGGER.warning("A warning message")
    time.sleep(1)
    LOGGER.error("An error message")
