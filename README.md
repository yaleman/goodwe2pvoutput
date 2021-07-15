Quick service for uploading data from your Goodwe inverter to PVOutput.org. 

It grabs generation (W), load (W), inverter temperature and voltage (V). If you're a subscriber to PVOutput you can store state of charge of your battery too. The data is pulled via my pygoodwe library in the [getDataPvOutput function](https://github.com/yaleman/pygoodwe/blob/master/pygoodwe/__init__.py#L236).

[![Build Status](https://droneio.yaleman.org/api/badges/yaleman/goodwe2pvoutput/status.svg)](https://droneio.yaleman.org/yaleman/goodwe2pvoutput)

# Configuration

File in one of these places:

* ~/.goodwe2pvoutput.conf (Home dir)
* ./goodwe2pvoutput.conf (Current dir)
* /etc/goodwe2pvoutput.conf

Template: see `goodwe2pvoutput.conf.example`

## Goodwe config

Determine the Station ID from the GOODWE site as follows. Open the [Sems Portal](https://www.semsportal.com). The Plant Status will reveal the Station ID in the URL. Example:

    https://www.semsportal.com/powerstation/powerstatussnmin/11112222-aaaa-bbbb-cccc-ddddeeeeeffff

Then the Station ID is `11112222-aaaa-bbbb-cccc-ddddeeeeeffff`.

## PVOutput config

Get your API key and system ID from [the account page on PVOutput](https://pvoutput.org/account.jsp)

# Running it

`goodwe2pvoutput` should do it for testing.

If you want to make it a `systemd` service:

* Download [goodwe2pvoutput.service](https://raw.githubusercontent.com/yaleman/goodwe2pvoutput/master/goodwe2pvoutput.service) to `/etc/systemd/system/` 
* Make sure the config file is at `/etc/goodwe2pvoutput.conf` 
* Run `sudo systemctl daemon-reload` to load the file
* `sudo systemctl status goodwe2pvoutput` to check it looks sane
* `sudo systemctl enable goodwe2pvoutput` to enable it on boot
* `sudo systemctl start goodwe2pvoutput` to start it


# Dependencies

* [pygoodwe](https://pypi.org/project/pygoodwe/)
* [pvoutput](https://pypi.org/project/pvoutput)
* [schedule](https://pypi.org/project/schedule/)

# Contributing

You're probably better off contributing to other packages like the dependencies above, but if you feel the need - [lodge an issue or PR on Github](https://github.com/yaleman/goodwe2pvoutput/issues)

# Changelog

* 0.0.1 Initial Version
* 0.0.2 2019-10-12 Updated to include SoC upload
* 0.0.3 2019-10-12 Turns out the "defaults" aren't as default as I thought in ConfigParser. Fixed.
* 0.0.4 2019-10-12 Way more config error checking
* 0.0.5 2021-01-08 Fixed the example config "systemid" field was mistyped.
* 0.0.6 2021-07-15 Didn't change the module much, added lambda function.