========
monorail
========

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


