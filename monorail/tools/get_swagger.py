#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 2 -*-
#
# monorail/tools/get_swagger.py -- gets all Swagger API schemas from the server
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
from json import dump
from os import makedirs
from os.path import exists, join


def get_swagger(username, password, output_dir):
  if not exists(output_dir):
    makedirs(output_dir)
  portal = OpenData(username, password)

  print('Getting service catalogue...')
  catalogue = portal.catalogs()
  
  for service in catalogue:
    slug_name = str(service['SsgUrl']).strip('*/').replace('/', '_') + '.json'
    print('Fetching %r...' % str(service['Name']))
    print('  %s' % slug_name)
    
    # Get the Swagger
    swagger = portal.swagger(service['Uuid'])
    
    # Write it out
    with open(join(output_dir, slug_name), 'wb') as f:
      dump(swagger, f, indent=2)

  print('All done!')

def main():
  parser = ArgumentParser()
  parser.add_argument('-u', '--username',
    required=True,
    help='Username to access the TfNSW portal')

  parser.add_argument('-p', '--password',
    required=True,
    help='Password to access the TfNSW portal')

  parser.add_argument('-o', '--output',
    required=True,
    help='Directory to output schemas into.  Will overwrite files.')

  options = parser.parse_args()
  get_swagger(options.username, options.password, options.output)

if __name__ == '__main__':
  main()

