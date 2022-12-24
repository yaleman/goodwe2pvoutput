"""

lambda function for doing the goodwe2pvoutput thing

"""
import logging
import os
from typing import Any, Dict

from pygoodwe import SingleInverter #type: ignore
from pvoutput import PVOutput #type: ignore
from pvoutput.parameters import ADDSTATUS_PARAMETERS #type: ignore

# pylint: disable=unused-argument,too-many-return-statements,too-many-branches
def lambda_handler(
    event: Dict[str,Any],
    context: Dict[str, Any],
) -> bool:
    """does the needful"""

    logger = logging.getLogger()

    if os.getenv("LOG_LEVEL") in [
        "CRITICAL",
        "ERROR",
        "WARNING",
        "INFO",
        "DEBUG",
        "NOTSET",
    ]:
        print(f"Setting log level to {os.getenv('LOG_LEVEL')}")
        logger.setLevel(getattr(logging, os.environ["LOG_LEVEL"]))
    else:
        logger.setLevel(logging.WARNING)

    ##################
    # Required environment variables
    ##################

    soc_field = os.getenv("SOC_FIELD")
    if soc_field is None:
        logger.error("Missing SOC_FIELD environment variable, bailing")
        return False
    soc_enable = bool(os.getenv("SOC_ENABLE"))
    pvoutput_donation_mode = os.getenv("PVOUTPUT_DONATION_MODE")
    pvoutput_apikey = os.getenv("PVOUTPUT_APIKEY")
    pvoutput_systemid_orig = os.getenv("PVOUTPUT_SYSTEMID")
    if pvoutput_systemid_orig is not None:
        pvoutput_systemid = int(pvoutput_systemid_orig)
    else:
        logger.error("Missing PVOUTPUT_SYSTEMID environment variable, bailing")
        return False

    goodwe_username = os.getenv("GOODWE_USERNAME")
    if goodwe_username is None:
        logger.error("Missing GOODWE_USERNAME environment variable, bailing")
        return False

    goodwe_password = os.getenv("GOODWE_PASSWORD")
    if goodwe_password is None:
        logger.error("Missing GOODWE_PASSWORD environment variable, bailing")
        return False
    goodwe_systemid = os.getenv("GOODWE_SYSTEMID")
    if goodwe_systemid is None:
        logger.error("Missing GOODWE_SYSTEMID environment variable, bailing")
        return False

    if None in [
        soc_enable,
        pvoutput_apikey,
        pvoutput_donation_mode,
    ]:
        logger.error("Missing environment variable, bailing")
        return False

    if soc_field not in ADDSTATUS_PARAMETERS:
        # setting an invalid field name
        print(
            f'Cannot log State of Charge to field "{soc_field}" - field does not exist'
        )
        soc_enable = False

    print("Instantiating PVOutput API Object")
    pvo = PVOutput(
        apikey=pvoutput_apikey,
        systemid=pvoutput_systemid,
        donation_made=pvoutput_donation_mode,
    )

    print("Connecting to Goodwe API")
    goodwe_inverter = SingleInverter(
        account=goodwe_username,
        system_id=goodwe_systemid,
        password=goodwe_password,
    )
    # update the data
    pvdata = goodwe_inverter.getDataPvoutput()

    if pvdata is None:
        logger.error("Couldn't get data from the system, bailing!")
        return False

    # add the state of charge data
    if soc_enable and pvoutput_donation_mode:
        pvdata[soc_field] = goodwe_inverter.get_battery_soc()
    elif soc_enable and not pvoutput_donation_mode:
        print("ENABLE_SOC flagged but not in donation mode, skipping.")

    # this'll throw errors if it's not right
    try:
        pvo.validate_data(pvdata, ADDSTATUS_PARAMETERS)
    except Exception as error_message:  # pylint: disable=broad-except
        print(f"PVOutput.validate_data({pvdata}) failed with an error: {error_message}")
        return False

    print(f"Grabbing the PVOutput-ready data: {pvdata}")

    print(f"Called the PVOutput addstatus endpoint: {pvo.addstatus(data=pvdata).text}")
    return True


if __name__ == "__main__":
    import sys

    print("This is not a shell script")
    sys.exit(1)
