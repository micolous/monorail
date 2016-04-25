********
monorail
********

A Python library for interfacing with `Transport for NSW's Open Data portal <https://opendata.transport.nsw.gov.au/>`_.

This is currently a work in progress.

Licensed under LGPLv3+.

Tools
=====

get_keys
--------

Shows all OAuth2 keys associated with your user account.

Usage::

	$ python -m monorail.tools.get_keys -u MyUsername -p MyPassword

Example output::

	You have 1 application(s) registered to 'MyUsername'.

		UUID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
		Name: My First Application
		 Key: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

get_swagger
-----------

Gets Swagger API schemas from the portal.  This will tool will dump all of the
available APIs for use into a directory.

Usage::

	$ python -m monorail.tools.get_swagger -u MyUsername -p MyPassword -o apis

These APIs can then be loaded into ``swagger-codegen`` with `some caveats <http://opendata.transport.nsw.gov.au/forum/t/swagger-api-schema-has-multiple-errors/94>`_::

	$ java -jar swagger-codegen-cli.jar generate -i apis/v1_gtfs_vehiclepos.json -l python -o apis/vehiclepos/

And then used with some Python code::

	#!/usr/bin/env python
	import swagger_client
	client = swagger_client.ApiClient(header_name='Authorization', header_value='Bearer xxxxx-xxxxxx-xxxxxxx-xxxxxxxxxx')

	# Trimming the / from the end
	client.host = client.host.rstrip('/')

	# Setup the SydneytrainsApi
	syd_trains = swagger_client.SydneytrainsApi(client)

	# Find all the trains!
	res = syd_trains.sydneytrains_res4_method0()

	# Print out the path to the protobuf blob
	print res

swaggify
--------

Refactors TfNSW's Swagger API in order to suck less:

1. Merges all the APIs into a single Swagger schema.
2. Real-time data APIs have consistent methods: ``alerts``, ``stop_times``, ``timetables``, ``vehicle_positions``.
3. Removes cruft from the end of method identifiers.
4. Makes all outputs ``file`` so that they can be actually used with the API.
5. Attempts to setup OAuth2 (but doesn't yet fully work).
6. Adds extra metadata to the schema to describe licensing and content-types.

See the template file for more details (``monorail/base_tfnsw_api.json``).

This requires that you have downloaded all the Swagger service descriptions
previously (using ``get_swagger``).

Example usage::

	$ python -m monorail.tools.swaggify -t monorail/base_tfnsw_api.json -o apis/tfnsw_api.json apis/v1_*.json
	$ java -jar swagger-codegen-cli.jar generate -i apis/tfnsw_api.json -o apis/tfnsw_api -l python -D packageName=tfnsw_api
	$ cd apis/tfnsw_api
	$ sudo python setup.py install
	$ python
	>>> import tfnsw_api
	>>> dir(tfnsw_api)
	['AlpineApi', 'ApiClient', 'BusesApi', 'CamerasApi', 'Configuration',
	'Error', 'EventsApi', 'FacilitiesandoperatorsApi', 'FerriesApi', 'FireApi',
	'FloodApi', 'GtfsApi', 'IncidentApi', 'LightrailApi', 'LoadingzonesApi',
	'MajoreventApi', 'NswtrainsApi', 'OffstreetparkingApi', 'ProgressApi',
	'RoadworkApi', 'RouteApi', 'StatusApi', 'SydneytrainsApi', 'TransxchangeApi',
	'__builtins__', '__doc__', '__file__', '__name__', '__package__', '__path__',
	'absolute_import', 'api_client', 'apis', 'configuration', 'models', 'rest']
	>>> tfnsw_api.Configuration().auth_settings = lambda: {'oauth2': {'in': 'header', 'key': 'Authorization', 'value': 'Bearer xxxxxxx'}}
	>>> syd_trains = tfnsw_api.SydneytrainsApi()
	>>> syd_trains.vehicle_positions()
	'/tmp/tmpXXXXXX'

`The generated Python bindings are also available <https://github.com/micolous/tfnsw_api_python>`_.

gtfs_realtime
-------------

Using the generated ``tfnsw_api`` from ``swaggify``, this tool will constantly
download timetables and real-time information from TfNSW.

This is useful for working with other applications, as the GTFS ZIP and
protobuf file will be saved in a folder for you to use.

Usage::

	$ python -m monorail.tools.gtfs_realtime -c 'client_id' -s 'client_secret' -o realtime

This will by default grab real-time data every minute, and grab timetable data
once per day.

This tool slows down the requests in order to not exhaust the low quotas on the
upstream server quickly.



