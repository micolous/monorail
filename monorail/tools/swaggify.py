#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 2 -*-
#
# monorail/tools/swaggify.py -- merges Swagger descriptions from the server
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

from argparse import ArgumentParser, FileType
from json import dump, load
from os import makedirs
from os.path import exists, join


def swaggify(input_schemas, template_file, output):
  # Load the template file first
  template = load(template_file)
  assert template['swagger'] == '2.0'
  root_path = template['basePath']
  
  # Now start processing the individual schemas
  for schema in input_schemas:
    schema = load(schema)
    assert schema['swagger'] == '2.0'
    assert schema['host'] == template['host']
    
    # Strip off trailing /, and shift it across to exclude the root.
    base_path = schema['basePath'].rstrip('/')
    assert base_path.startswith(root_path)
    base_path = base_path[len(root_path):]
    
    # Figure out the default content type
    content_type = None
    for tag in schema['tags']:
      if tag['name'] not in (x['name'] for x in template['tags']):
        template['tags'].append(tag)

    # Iterate through paths
    for path_str, handler in schema['paths'].iteritems():
      path_str = base_path + '/' + path_str.lstrip('/')

      for method, action in handler.iteritems():
        for err, outf in action['responses'].iteritems():
          if '$ref' in outf['schema'] and outf['schema']['$ref'] == '#/definitions/Response':
            del outf['schema']['$ref']
            outf['schema']['type'] = 'file'

        # Set correct content-types
        description = action['description'].lower()

        content_type = None
        if 'geojson' in description:
          content_type = 'application/vnd.geo+json'
        elif 'developers.google.com/transit/gtfs-realtime/' in description:
          content_type = 'application/octet-stream'
        elif 'developers.google.com/transit/gtfs/' in description or 'www.transxchange.org.uk' in description:
          content_type = 'application/zip'

        if content_type:
          action['produces'] = [content_type]

        # Fix operationId to suck less
        operationId = action['operationId']
        summary = action['summary'].lower()
        
        if 'realtime stop time update' in summary:
          operationId = 'stopTimes'
        elif 'realtime vehicle positions' in summary:
          operationId = 'vehiclePositions'
        elif 'realtime alerts' in summary:
          operationId = 'alerts'
        elif 'gtfs timetables' in summary:
          operationId = 'timetables'
        else:
          if operationId.startswith('Trains_'):
            operationId = 'SydneyTrains'
          operationId = operationId.replace('sydneytrains', 'SydneyTrains')
          operationId = operationId.replace('NSW', 'Nsw')
          if operationId.lower().startswith('get'):
          	 operationId = operationId[3:]
          
          if len(operationId.split('_')) > 2:
            operationId = '_'.join(operationId.split('_')[:-2])
        
        action['operationId'] = operationId
    
      # We've patched up the path, lets drop it in
      template['paths'][path_str] = handler

  # We've done all the files, now write it out.
  dump(template, output, indent=2)

def main():
  parser = ArgumentParser()

  parser.add_argument('-o', '--output',
    required=True,
    type=FileType('wb'),
    help='File to output schema into.  Will overwrite file.')

  parser.add_argument('input_schemas',
    nargs='+',
    type=FileType('rb'),
    help='Input schema files')

  parser.add_argument('-t', '--template-file',
    required=True,
    type=FileType('rb'),
    help='Template schema to use as the base')

  options = parser.parse_args()
  swaggify(options.input_schemas, options.template_file, options.output)

if __name__ == '__main__':
  main()

