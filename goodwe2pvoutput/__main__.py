#!/usr/bin/env python

<<<<<<< HEAD
import logging
import sys
import time
from pathlib import Path
from typing import Any, Self
=======
import sys
import time
from typing import Any
>>>>>>> origin/main

import schedule
from pvoutput import PVOutput
from pvoutput.exceptions import InvalidRegexpError
from pvoutput.parameters import ADDSTATUS_PARAMETERS
<<<<<<< HEAD
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings
from pygoodwe import SingleInverter

FORMAT = "%(asctime)-15s %(message)s"
logging.basicConfig(format=FORMAT)

logger = logging.getLogger()


CONFIG_FILES = [
    "./goodwe2pvoutput.json",
    "/etc/goodwe2pvoutput.json",
    f"{Path.home()!s}/.goodwe2pvoutput.json",
]


class Config(BaseSettings):
    logging_level: str = Field("INFO", description="Logging level")

    goodwe_account: str = Field(description="Goodwe account email")
    goodwe_password: str = Field(description="Goodwe account password")
    goodwe_systemid: str = Field(description="Goodwe account systemd ID")

    schedule_minutes: int = Field(10, description="Schedule time in minutes")

    pvoutput_apikey: str = Field(description="PVOutput API key")
    pvoutput_systemid: int = Field(description="PVOutput system ID")
    pvoutput_donation_made: bool = Field(
        False, description="Donation made to PVOutput, enable extra fields"
    )
    pvoutput_soc_enable: bool = Field(
        False, description="Enable State of Charge logging"
    )
    pvoutput_soc_field: str | None = Field(
        default=None, description="State of Charge field name"
    )

    @field_validator("logging_level")
    @classmethod
    def check_logging_level(cls, v: str) -> str:
        if v.upper() not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]:
            raise ValueError(f"Invalid logging level: {v}")
        return v.upper()

    @model_validator(mode="after")
    def check_soc_field(self) -> Self:
        if self.pvoutput_soc_enable and not self.pvoutput_donation_made:
            raise ValueError("Cannot log State of Charge if you have not donated")
        if (
            self.pvoutput_soc_field is not None
            and self.pvoutput_soc_field not in ADDSTATUS_PARAMETERS
        ):
            raise ValueError(
                f'Cannot log State of Charge to field "{self.pvoutput_soc_field}" - field does not exist'
            )
        return self

    @classmethod
    def load(cls) -> "Config":
        for file in CONFIG_FILES:
            if Path(file).exists():
                logger.debug("Reading config file: %s", file)
                return Config.model_validate_json(Path(file).read_text())
        logger.debug("No config file found, quitting!")
        sys.exit(1)


config = Config.load()

logger.setLevel(config.logging_level.upper())
=======
from pygoodwe import SingleInverter

from goodwe2pvoutput import LOGGER, Config
>>>>>>> origin/main


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
<<<<<<< HEAD
    except Exception as e:  # noqa: BLE001
        logger.error("PVOutput.validate_data(%s) failed with an error: %s", pvdata, e)
=======
    except (TypeError, ValueError, InvalidRegexpError) as e:
        LOGGER.error("PVOutput.validate_data(%s) failed with an error: %s", pvdata, e)
>>>>>>> origin/main
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
