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

	$ java -jar swagger-codegen-cli.jar generate -i swag/v1_gtfs_vehiclepos.json -l python -o swag/vehiclepos/

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


