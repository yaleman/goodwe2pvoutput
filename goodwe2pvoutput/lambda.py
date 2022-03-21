"""

lambda function for doing the goodwe2pvoutput thing

"""
import os
import logging

from pygoodwe import SingleInverter
from pvoutput import PVOutput
from pvoutput.parameters import ADDSTATUS_PARAMETERS

# pylint: disable=unused-argument
def lambda_handler(
    event: dict, context: dict
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
    soc_enable = bool(os.getenv("SOC_ENABLE"))
    pvoutput_donation_mode = os.getenv("PVOUTPUT_DONATION_MODE")
    pvoutput_apikey = os.getenv("PVOUTPUT_APIKEY")
    pvoutput_systemid_orig = os.getenv("PVOUTPUT_SYSTEMID")
    if pvoutput_systemid_orig is not None:
        pvoutput_systemid = int(pvoutput_systemid_orig)

    goodwe_username = os.getenv("GOODWE_USERNAME")
    goodwe_password = os.getenv("GOODWE_PASSWORD")
    goodwe_systemid = os.getenv("GOODWE_SYSTEMID")
    if None in [
        soc_field,
        soc_enable,
        pvoutput_apikey,
        pvoutput_donation_mode,
        pvoutput_systemid_orig,
        goodwe_password,
        goodwe_systemid,
        goodwe_username,
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
