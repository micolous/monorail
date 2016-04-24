#!/usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; tab-width: 2 -*-
#
# monorail/opendata.py - Library for scraping opendata.transport.nsw.gov.au
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

import requests
from time import time

OPENDATA_ROOT = 'https://opendata.transport.nsw.gov.au/'
STD_HEADERS = {'User-Agent': 'monorail/0.1'}
JSON_HEADER = {'Accept': 'application/json'}

OPENDATA_LOGIN_URL = OPENDATA_ROOT + 'admin/j_spring_security_check'
OPENDATA_DASHBOARD = OPENDATA_ROOT + 'app/dashboard.html'
OPENDATA_LOGIN_FORM = OPENDATA_ROOT + 'app/login.html'
OPENDATA_SESSION_CHECK = OPENDATA_ROOT + 'admin/sessionCheck'
OPENDATA_CATALOGS = OPENDATA_ROOT + 'admin/Portal.svc/ApiCatalogs'
OPENDATA_APPLICATIONS = OPENDATA_ROOT + 'admin/Portal.svc/Applications'
OPENDATA_SWAGGER = OPENDATA_ROOT + 'admin/apidescriptor/%s/swagger'
OPENDATA_DIRECT = OPENDATA_ROOT + 'direct/'

DIRECT_GTFS = 'full_greater_sydney_gtfs_static.zip'
DIRECT_TXC = 'transxchange.zip'
DIRECT_FACILITIES = 'Location_Facilities_Data.zip'
DIRECT_PARKING = 'OffstreetparkingData.zip'
DIRECT_LOADING = 'LoadingzoneData.zip'


class OpenData(object):
  def __init__(self, username, password):
    """
    Creates a session for working with the Transport for NSW Open Data portal.

    Authentication is not attempted immediately.

    :param username: The username to use when authenticating to the portal.
    :param password: The password to use when authenticating to the portal.
    """
    self._username = username
    self._password = password
    self._session = requests.Session()
    self._session.headers = STD_HEADERS


  def session_check(self):
    """
    Checks whether our session cookies are valid.
    
    This endpoint also sets the "gateaugage" cookie which is used for API
    service descriptor endpoints.
    
    Returns True if they are valid, False otherwise.
    """
    response = self._session.get(OPENDATA_SESSION_CHECK, allow_redirects=False)
    
    return response.status_code == 200
    

  def login(self, username=None, password=None):
    """
    Logs in to the Open Data portal.
    
    If ``username`` or ``password`` are specified, this is used instead of the
    values passed in to the constructor.  If authentication is successful, these
    will overwrite the stored value from the constructor.
    
    Thrown ``Exception`` in the case of an authentication fault.
    
    :param username: Username to authenticate with.
    :param password: Password to authenticate with.
    """
    if not username:
      username = self._username
    if not password:
      password = self._password

    if not username or not password:
      raise Exception, 'Username and password is required to log in.'

    # https://opendata.transport.nsw.gov.au/admin/j_spring_security_check
    # takes POST parameter "username" and "password"
    response = self._session.post(OPENDATA_LOGIN_URL, params=dict(username=username, password=password), allow_redirects=False)
    
    assert response.status_code == 302
    if response.headers['Location'].startswith(OPENDATA_LOGIN_FORM):
      # Login probably incorrect
      raise Exception, 'Invalid authentication details.'

    # The login cookies are now stored.

    # Overwrite stored username and password so we can re-auth later
    # Sessions are very short on the server.
    self._username = username
    self._password = password


  def catalogs(self):
    """
    Gets a catalogue of APIs from the portal.
    
    The catalogue will be a list containing dicts of the following schema::
    
      {
        'SsgUrl': The root of the API's URLs, with no trailing slash.
        'Name': A human readable name for the API.
        'Description': A longer description of the API.
        'Uuid': The API's UUID.
      }
    """
    if not self.session_check():
      self.login()
      assert self.session_check()

    response = self._session.get(OPENDATA_CATALOGS, params={
      '$select': 'Uuid,Name,Description,SsgUrl',
      '$inlinecount': 'allpages',
      '$filter': 'SpecFilesize gt 0 and PortalStatus eq \'ENABLED\''
    }, headers=JSON_HEADER, allow_redirects=False)

    result = response.json()
    
    if 'd' not in result:
      return []

    return result['d']['results']


  def swagger(self, api_uuid):
    """
    Gets a Swagger 2.0 service description for the API endpoint.
    
    Documentation of the Swagger specification is available at:
    https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md
    """
    api_uuid = str(api_uuid)
    if not self.session_check():
      self.login()
      assert self.session_check()

    response = self._session.get((OPENDATA_SWAGGER % api_uuid), headers=JSON_HEADER, allow_redirects=False)
    result = response.json()
    return result


  def applications(self, api_uuid=None):
    """
    Gets a list of applications (API keys).
    
    :param api_uuid: Only select applications which have the following API UUID enabled for them.
    """
    if not self.session_check():
      self.login()
      assert self.session_check()
    
    response = self._session.get(OPENDATA_APPLICATIONS, params={
      '$select': 'Uuid,Name,Description,ApiKey,KeySecret',
      '$inlinecount': 'allpages',
      '$filter': ((('ApiUuid eq %r and ' % str(api_uuid)) if api_uuid else '') +
                  'Status eq \'ENABLED\'')
    }, headers=JSON_HEADER, allow_redirects=False)
    
    result = response.json()
    
    if 'd' not in result:
      return []

    return result['d']['results']


  def direct_download(self, filename):
    """
    Allows direct downloads of static resources.
    """
    if not self.session_check():
      self.login()
      assert self.session_check()

    return self._session.get(OPENDATA_DIRECT + filename, allow_redirects=False)


  def direct_gtfs(self):
    """
    Requests the static GTFS data.
    """
    return self.direct_download(DIRECT_GTFS)


  def direct_txc(self):
    """
    Requests the TransXChange data.
    """
    return self.direct_download(DIRECT_TXC)

    
  def direct_facilities(self):
    """
    Requests the Facilities and Operators data.
    """
    return self.direct_download(DIRECT_FACILITIES)

  
  def direct_parking(self):
    """
    Requests the Off-street Parking data.
    """
    return self.direct_download(DIRECT_PARKING)


  def direct_loading(self):
    """
    Requests the Loading Zone data.
    """
    return self.direct_download(DIRECT_LOADING)

