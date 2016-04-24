#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 2 -*-
#
# monorail/tools/get_keys.py -- gets all application keys from the TfNSW portal
# Copyright 2016 Michael Farrell <micolous+git@gmail.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import, print_function
from ..opendata import OpenData

from argparse import ArgumentParser


def get_keys(username, password, no_secret):
  portal = OpenData(username, password)
  apps = portal.applications()
  
  print('You have %d application(s) registered to %r.' % (len(apps), username))
  print('')

  for app in apps:
    print('   UUID: %s' % app['Uuid'])
    print('   Name: %s' % app['Name'])
    print('    Key: %s' % app['ApiKey'])
    if not no_secret:
      print(' Secret: %s' % app['KeySecret'])
    print('')


def main():
  parser = ArgumentParser()
  parser.add_argument('-u', '--username',
    required=True,
    help='Username to access the TfNSW portal')

  parser.add_argument('-p', '--password',
    required=True,
    help='Password to access the TfNSW portal')

  parser.add_argument('-n', '--no-secret',
    action='store_true',
    help='Don\'t display the application\'s secret key')

  options = parser.parse_args()
  get_keys(options.username, options.password, options.no_secret)

if __name__ == '__main__':
  main()

