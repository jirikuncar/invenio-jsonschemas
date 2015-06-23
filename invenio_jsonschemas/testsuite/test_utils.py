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

from __future__ import print_function, unicode_literals

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite


class UtilsTest(InvenioTestCase):
    def test_urljoin(self):
        from invenio_jsonschemas.utils import urljoin

        self.assertEqual(
            urljoin('http://test.org'),
            'http://test.org',
            'touches normal URL'
        )
        self.assertEqual(
            urljoin('http://test.org', 'foo'),
            'http://test.org/foo',
            'cannot do a simple append'
        )
        self.assertEqual(
            urljoin('http://test.org', 'foo/'),
            'http://test.org/foo/',
            'does not respect trailing slash'
        )
        self.assertEqual(
            urljoin('http://test.org/', 'foo'),
            'http://test.org/foo',
            'does not handle trailing slash in first component correctly'
        )
        self.assertEqual(
            urljoin('http://test.org', '/foo'),
            'http://test.org/foo',
            'does not handle leading slash in second component correctly'
        )
        self.assertEqual(
            urljoin('http://test.org/', '/foo'),
            'http://test.org/foo',
            'does not handle trailing + leading slash correctly'
        )
        self.assertEqual(
            urljoin('http://test.org/', 'foo', 'bar'),
            'http://test.org/foo/bar',
            'does not handle 3 components'
        )
        self.assertEqual(
            urljoin('http://test.org/', 'foo', 'bar', 'x', 'y', 'z'),
            'http://test.org/foo/bar/x/y/z',
            'does not handle 6 components'
        )
        self.assertEqual(
            urljoin(),
            '',
            'does not handle zero components'
        )
        self.assertEqual(
            urljoin('http://test.org/', '/foo?p=1'),
            'http://test.org/foo?p=1',
            'does not handle query parameters correctly'
        )
        self.assertEqual(
            urljoin('http://test.org/', '/foo#bar'),
            'http://test.org/foo#bar',
            'does not handle fragments correctly'
        )


TEST_SUITE = make_test_suite(UtilsTest)

if __name__ == '__main__':
    run_test_suite(TEST_SUITE)
