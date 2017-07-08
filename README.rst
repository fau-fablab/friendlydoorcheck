===================
Friendly Door Check
===================

This service checks a google calendar for events that require the space's door to be open and matches it with the space's spaceapi. It sends out an alert mail in case the space is closed during open events. It also sends a recovery notice once the problem has resolved.

Requirements
============
* google-api-python-client
* requests
* ruamel.yaml
* pytz

Installation and Configuration
==============================
1. Create a project and an API key in the `Google API Console<https://console.developers.google.com>`_
2. Place client_id.json (obtained from API Console) file in this project directory
3. Run ``./fdc.py --noauth_local_webserver example.yml`` and follow instructions to authenticate access to google account's calendars
4. Have a look at ``example.yml`` and configure appropriately

Usage
=====
Execute:
::
    ./fdc.py config.yml

Continues to run until no more suitable events (matching regex, end in future and not full-day events) can be retrieved from google.
