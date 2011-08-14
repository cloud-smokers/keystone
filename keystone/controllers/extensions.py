import os
import sys
from webob import Response

# If ../../keystone/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                   os.pardir,
                                   os.pardir))

from keystone import utils
from keystone.common import template, wsgi
import keystone.config as config


class ExtensionsController(wsgi.Controller):
    """Controller for extensions related methods"""

    def __init__(self, options):
        self.options = options

    @utils.wrap_error
    def  get_extensions_info(self, req, path):
        resp = Response()

        if utils.is_xml_response(req):
            resp_file = "%s.xml" % path
            mime_type = "application/xml"
        else:
            resp_file = "%s.json" % path
            mime_type = "application/json"

        print resp_file
        return template.static_file(resp, req, resp_file,
                root=utils.get_app_root(), mimetype=mime_type)
