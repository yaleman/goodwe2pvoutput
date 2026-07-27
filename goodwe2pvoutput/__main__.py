#!/usr/bin/env python

import sys
import time
from typing import Any

import schedule
from pvoutput import PVOutput
from pvoutput.exceptions import InvalidRegexpError
from pvoutput.parameters import ADDSTATUS_PARAMETERS
from pygoodwe import SingleInverter

from goodwe2pvoutput import LOGGER, Config


def add_soc(
    config: Config, gw: SingleInverter, pvo: PVOutput, pvdata: dict[str, Any]
) -> dict[str, Any]:
    """adds the state of charge field if you've donated and set it to"""
    if not config.pvoutput_soc_enable:
        return pvdata
    if not config.pvoutput_donation_made:
        return pvdata
    if config.pvoutput_soc_field is not None:
        pvdata[config.pvoutput_soc_field] = gw.get_battery_soc()

    # this'll throw errors if it's not right
    try:
        pvo.validate_data(pvdata, ADDSTATUS_PARAMETERS)
    except (TypeError, ValueError, InvalidRegexpError) as e:
        LOGGER.error("PVOutput.validate_data(%s) failed with an error: %s", pvdata, e)
        sys.exit(1)
    return pvdata


def do_the_thing(config: Config) -> None:
    LOGGER.debug("Starting do_the_thing()")

    LOGGER.debug("Instantiating PVOutput API Object")
    pvo = PVOutput(
        apikey=config.pvoutput_apikey.get_secret_value(),
        systemid=config.pvoutput_systemid,
        donation_made=config.pvoutput_donation_made,
    )

    LOGGER.debug("Connecting to Goodwe API")
    gw = SingleInverter(
        system_id=config.goodwe_systemid,
        account=config.goodwe_username,
        password=config.goodwe_password.get_secret_value(),
    )
    # update the data
    gw.get_current_readings(maxretries=0)

    pvdata = gw.getDataPvoutput()
    # add the state of charge data
    if config.dry_run:
        LOGGER.info("Dry run, not sending data to PVOutput: %s", pvdata)
        return
    pvdata = add_soc(config, gw, pvo, pvdata)
    LOGGER.debug("Grabbing the PVOutput-ready data: %s", pvdata)

    response = pvo.addstatus(data=pvdata)
    LOGGER.debug("Called the PVOutput addstatus endpoint: %s", response.text)


def main() -> None:
    # simple scheduler, run do_the_thing() every x minutes

    config = Config()
    LOGGER.setLevel(config.logging_level.upper())

    if config.show_config:
        LOGGER.info("Config dump:")
        for key, value in config.model_dump().items():
            LOGGER.info("%s: %s", key, value)
        return

    LOGGER.debug("Scheduling update every %s minutes", config.schedule_minutes)
    schedule.every(config.schedule_minutes).minutes.do(do_the_thing)

    LOGGER.debug("Doing initial run...")
    do_the_thing(config)

    LOGGER.debug("Running scheduler...")
    while True:
        time.sleep(5)
        schedule.run_pending()


if __name__ == "__main__":
    main()
