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

"""Views provided by Invenio JSONSchemas."""

import os
import os.path

from collections import OrderedDict

from flask import Blueprint, current_app, render_template

from flask_breadcrumbs import register_breadcrumb

from invenio.base.i18n import _

from .utils import internal_schema_url


blueprint = Blueprint(
    'jsonschemas',
    __name__,
    url_prefix='/jsonschemas',
    static_folder='static',
    template_folder='templates',
)


@blueprint.route('/', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.jsonschemas', _('JSON Schemas'))
def index():
    """Render schema index with all known schema files."""
    schema_path_generated = os.path.join(
        current_app.static_folder,
        'gen',
        'jsonschemas'
    )

    def _split_path(string):
        """Split path string into an array.

        The result depends on `os.path.split`.
        """
        result = []
        while string:
            head, tail = os.path.split(string)
            result.insert(0, tail)
            string = head
        return result

    def _tree_insert(tree, path, element):
        """Add element into a dict tree.

        After finding and creating the path and node that is the target of
        this operation, the element will be inserted into a list that is
        located in the `'.'` subkey. Example:

        .. code:: python

            tree = {
                '.': ['README.md', 'LICENSE'],
                'src': {
                    '.': ['Makefile'],
                    'lib': {
                        'xx': {
                            '.': ['foo.c']
                        }
                    }
                },
                'doc': {
                    '.': ['changelog.md']
                }
            }
            element1 = 'bar.c'
            element2 = 'hello.c'
            path1 = ['src', 'lib', 'xx']
            path2 = ['src', 'cmd', 'manage']
            _tree_insert(tree, path1, element1)
            _tree_insert(tree, path2, element2)

            tree == {
                '.': ['README.md', 'LICENSE'],
                'src': {
                    '.': ['Makefile'],
                    'lib': {
                        'xx': {
                            '.': ['foo.c', 'bar.c']
                        }
                    },
                    'cmd': {
                        'manage': {
                            '.': ['hello.c']
                        }
                    }
                },
                'doc': {
                    '.': ['changelog.md']
                }
            }

        Note that dicts in python are not ordered.

        :param tree: the root of the dict tree
        :param path: a list representing the path in the tree
        :param element: element that should be inserted.
        """
        if path:
            current = path.pop(0)
            if current not in tree:
                tree[current] = dict()
            _tree_insert(tree[current], path, element)
        else:
            if '.' not in tree:
                tree['.'] = list()
            tree['.'].append(element)

    def _tree_sort(tree):
        """Sort dict tree and the list in `'.'` nodes.

        Dicts will be converted into `OrderedDict`. `'.'` will be before all
        other nodes.

        Example:

        .. code:: python

            tree = {
                '.': ['README.md', 'LICENSE'],
                'src': {
                    '.': ['Makefile'],
                    'lib': {
                        'xx': {
                            '.': ['foo.c', 'bar.c']
                        }
                    },
                    'cmd': {
                        'manage': {
                            '.': ['hello.c']
                        }
                    }
                },
                'doc': {
                    '.': ['changelog.md']
                }
            }

            otree = _tree_sort(tree)

            otree == OrderedDict(
                '.'=['LICENSE', 'README.md'],
                'doc'=OrderedDict(
                    '.'=['changelog.md']
                ),
                'src'=OrderedDict(
                    '.'=['Makefile'],
                    'cmd'=OrderedDict(
                        'manage'=OrderedDict(
                            '.'=['hello.c']
                        )
                    ),
                    'lib'=OrderedDict(
                        'xx'=OrderedDict(
                            '.'=['bar.c', 'foo.c']
                        )
                    )
                )
            )
        """
        result = OrderedDict()
        if '.' in tree:
            sub = tree.pop('.')
            result['.'] = list(sorted(sub, key=lambda e: e['name']))
        for k in sorted(tree.iterkeys()):
            result[k] = _tree_sort(tree[k])
        return result

    tree = dict()
    for root, dirs, files in os.walk(schema_path_generated):
        for name in files:
            path = _split_path(os.path.relpath(root, schema_path_generated))
            _tree_insert(tree, path, {
                'name': name,
                'link': internal_schema_url(*(path + [name]))
            })

    return render_template('jsonschemas/schema.html', tree=_tree_sort(tree))


@blueprint.route('/<path:path>')
def schema(path):
    """Serve static schema file."""
    return current_app.send_static_file(
        os.path.join('gen', 'jsonschemas', path)
    )
