#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 2 -*-
#
# monorail/tools/gtfs_realtime.py - Leeches the gtfs-realtime data into a directory continually
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

from __future__ import print_function

from argparse import ArgumentParser
from datetime import datetime, timedelta
from os import makedirs
from os.path import exists, join
import requests
from shutil import move
from time import sleep
import tfnsw_api



def get_oauth_token(client_id, client_secret):
  """
  Gets an OAuth2 bearer token using an Application flow from the API server.
  
  Returns a tuple of token, type, expiry(UTC)
  """
  response = requests.post('https://api.transport.nsw.gov.au/auth/oauth/v2/token?scope=user&grant_type=client_credentials',
    auth=(client_id, client_secret), data='')
  
  assert response.status_code == 200, 'unexpected response code (%d)' % response.status_code
  response = response.json()
  
  # Parse the result
  access_token = response['access_token']
  token_type = response['token_type']
  expiry = datetime.utcnow() + timedelta(seconds=int(response['expires_in']))
  return access_token, token_type, expiry


def gtfs_realtime(client_id, client_secret, output_dir, frequency):
  if not exists(output_dir):
    makedirs(output_dir)

  next_update = None
  access_token = token_type = expiry = None
  update_num = 0

  apis = {
    'sydtrains': tfnsw_api.SydneytrainsApi(),
    #'nswtrains': tfnsw_api.NswtrainsApi(),
    'lightrail': tfnsw_api.LightrailApi(),
    'ferries': tfnsw_api.FerriesApi(),
    #'buses': tfnsw_api.BusesApi(),
  }
  
  # now run a loop!
  while True:
    try:
      # Wait a bit for next update
      while (next_update is not None and next_update > datetime.utcnow()):
        sleep(0.5)
      
      # Record the start of our execution
      loop_start = datetime.utcnow()
      print('starting loop')
      
      # Check if we need to refresh
      if not expiry or expiry < (datetime.utcnow() + timedelta(seconds=frequency*5)):
        # We need to refresh
        print('refreshing access token')
        access_token, token_type, expiry = get_oauth_token(client_id, client_secret)

        tfnsw_api.Configuration().auth_settings = lambda: {'oauth2': {
          'in': 'header',
          'key': 'Authorization',
          'value': ('%s %s' % (token_type, access_token))
        }}
      
      # Start fetching the different APIs
      print('fetching apis')
      
      for mode, api in apis.iteritems():
        print ('...%s' % mode)
        if mode == 'sydtrains':
          alerts = api.alerts()
          move(alerts, join(output_dir, mode + '_alerts.pb'))
          sleep(1)

        stop_times = api.stop_times()
        move(stop_times, join(output_dir, mode + '_stops.pb'))
        sleep(1)

        vehicle_positions = api.vehicle_positions()
        move(vehicle_positions, join(output_dir, mode + '_pos.pb'))
        sleep(1)
      
        if update_num == 0:
          print('Also fetching timetable')
          # Every day, fetch the timetables
          timetables = api.timetables()
          move(timetables, join(output_dir, mode + '_tt.zip'))
          sleep(1)
      
      # Schedule next update
      next_update = loop_start + timedelta(seconds=frequency)
      update_num += 1
      if update_num > 3600:
        update_num = 0
      print('Done, waiting for next run')
    except KeyboardInterrupt:
      break

def main():
  parser = ArgumentParser()
  parser.add_argument('-c', '--client-id',
    required=True,
    help='Client ID (api key) to use to authenticate.')
  
  parser.add_argument('-s', '--client-secret',
    required=True,
    help='Client Secret (shared secret) to use to authenticate.')

  parser.add_argument('-o', '--output-dir',
    required=True,
    help='Output directory for feed files.')
  
  parser.add_argument('-f', '--frequency',
    type=int,
    help='Wait this many seconds between updates [default: %(default)s]',
    default=60)

  options = parser.parse_args()
  gtfs_realtime(options.client_id, options.client_secret, options.output_dir, options.frequency)


if __name__ == '__main__':
  main()

