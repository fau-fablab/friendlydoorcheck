===================
Friendly Door Check
===================

This service checks an ical feed for events and matches it with the spaces API and sends out an alert mail in case of closed space during open events.

Requirements
============
* icalendar
* requests
* ruamel.yaml

Usage
=====
    ./fdc.py ical_url spaceapi_url seconds_allowed_diff poll_during_open_time title_regex
