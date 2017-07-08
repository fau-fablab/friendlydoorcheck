===================
Friendly Door Check
===================

This service checks an ical feed for events and matches it with the spaces API and sends out an alert mail in case of closed space during open events.

Requirements
============
* google-api-python-client
* requests
* ruamel.yaml

Usage
=====
    ./fdc.py config

If started on a remote machine using ssh, use `--noauth_local_webserver` flag on first start.
