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

"""Bundles for Invenio JSONSchemas."""

from __future__ import unicode_literals

import json
import os
import os.path

from flask import current_app

from webassets.filter import Filter

from .utils import internal_schema_url


__all__ = (
    'JSONOptimize',
    'SchemaAllof',
)


class JSONOptimize(Filter):

    """Optimize JSON.

    Strip newlines and unrequired whitespaces.
    """

    name = 'json_optimize'

    def output(self, _in, out, **kwargs):
        """Output filter, does the job of optimizing."""
        j = json.loads(_in.read())
        out.write(
            json.dumps(
                j,
                separators=(',', ':')
            )
        )


class SchemaAllof(Filter):

    """Combine multiple JSON schemas using `allOf`."""

    name = 'schema_allof'

    def input(self, _in, out, **kwargs):
        """Input filter, that transforms schemas into their URLs."""
        schema = kwargs['source_path']

        out.write('{"$ref":"')
        out.write(internal_schema_url(
            os.path.relpath(
                schema,
                os.path.join(
                    current_app.static_folder,
                    'jsonschemas'
                )
            )
        ))
        out.write('"},')

    def output(self, _in, out, **kwargs):
        """Output filter, that does the boilerplate."""
        out.write('{')
        out.write('"allOf": [')

        s = _in.read()
        if s.endswith(','):
            s = s[:-1]
        out.write(s)

        out.write(']')
        out.write('}')
