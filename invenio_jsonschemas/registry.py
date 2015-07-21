# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

import os

from flask_registry import PkgResourcesDirDiscoveryRegistry, \
    RegistryProxy


class RecursiveDirDiscoveryRegistry(PkgResourcesDirDiscoveryRegistry):

    def register(self, path):
        prefix, filename = path.rsplit(os.path.sep, 1)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    subpath = os.path.join(root, f)
                    subfile = os.path.join(filename, f)
                    super(RecursiveDirDiscoveryRegistry, self).register(
                        (subfile, subpath)
                    )
        else:
            return super(RecursiveDirDiscoveryRegistry, self).register(
                (filename, path)
            )

jsonschemas = RegistryProxy(
    'jsonschemas', RecursiveDirDiscoveryRegistry, 'jsonschemas'
)
