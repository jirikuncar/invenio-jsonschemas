# -*- coding: utf-8 -*-
#
# This file is part of Invenio JSONSchemas.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Different utils for JSON handling."""

import copy
import json
import os.path
import urlparse

from flask import current_app, url_for

from jsonpointer import resolve_pointer

import jsonschema

from speaklater import _LazyString


class InsecureSchemaLocation(Exception):

    """The try to load a JSON schema from an insecure location."""

    pass


def urljoin(*args):
    """Join parts of a URL together, similar to `os.path.join`."""
    def _add_trailing_slash(s):
        if s.endswith('/'):
            return s
        else:
            return s + '/'

    if len(args) > 1:
        result = reduce(urlparse.urljoin, map(_add_trailing_slash, args[:-1]))
    else:
        result = ''

    if len(args) > 0:
        result = urlparse.urljoin(
            result,
            args[-1]
        )

    return result


def internal_schema_url(*parts):
    """Return the URL to an internal JSON schema."""
    return url_for('jsonschemas.schema', path=os.path.join(*parts), _external=True)


def ensure_subpath(path):
    """Santize given path to be a subpath, e.g. not traversing up.

    The returned path will not contain any upwards traversal using `..` and
    therefore can safely appended to a basepath.

    .. caution::
        This does **NOT** protect against symlink based traversal!
    """
    # http://www.guyrutenberg.com/2013/12/06/preventing-directory-traversal-in-python/
    return os.path.normpath('/' + path).lstrip('/')


def get_schema(uri):
    """Get and parse a JSON schema from the given URI.

    Internal schemas are loaded from the file system. Caching may apply for
    internal and external schemas. JSON pointers given as fragment of the URI
    are supported.
    """
    # split the fragment
    uri_parsed = urlparse.urlparse(uri)

    # 1. interal resource?
    base = url_for('jsonschemas.schema', path='', _external=True)
    base_parsed = urlparse.urlparse(base)
    if base_parsed.scheme == uri_parsed.scheme \
            and base_parsed.netloc == uri_parsed.netloc \
            and uri_parsed.path.startswith(base_parsed.path):
        internal_path = uri_parsed.path.split(base_parsed.path, 1)[1]

        with open(os.path.join(
                current_app.static_folder,
                'gen',
                'jsonschemas',
                ensure_subpath(internal_path))
                ) as f:
            return resolve_pointer(
                json.loads(f.read()),
                uri_parsed.fragment
            )

    # 2. external resource
    # FIXME support whitelisting of secure location
    raise InsecureSchemaLocation(
        'Requested schema located on insecure location: ' + uri
    )


def validate_json(json, schema=None, additional_properties=None):
    """Validate JSON against a given schema.

    If no schema is provided, the `$schema` attribute of the JSON object will
    be used. In both cases, schema URIs and parsed schemas are supported.
    """
    # should we get the schema from the JSON itself?
    if not schema:
        schema = json.get('$schema', {})

    # is the schema a link or the parsed schema?
    if isinstance(schema, basestring) or isinstance(schema, _LazyString):
        schema = get_schema(schema)

    # allow additional properties?
    if additional_properties is not None:
        schema['additionalProperties'] = additional_properties

    # remove `$schema`, because jsonschema does not handle or ignore it
    # instead it would result in an validation error
    data = copy.deepcopy(json)
    data.pop('$schema', None)

    jsonschema.validate(data, schema)
    return True
