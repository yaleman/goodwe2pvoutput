"""

lambda function for doing the goodwe2pvoutput thing

"""
import os
import logging


from pygoodwe import SingleInverter
from pvoutput import PVOutput
from pvoutput.parameters import ADDSTATUS_PARAMETERS

def lambda_handler(event: dict, context: dict) -> bool:
    """ does the needful """

    logger = logging.getLogger()

    if os.getenv('LOG_LEVEL') in ['CRITICAL','ERROR','WARNING','INFO','DEBUG','NOTSET']:
        print(f"Setting log level to {os.getenv('LOG_LEVEL')}")
        logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL')))
    else:
        logger.setLevel(logging.WARNING)

    ##################
    # Required environment variables
    ##################
    SOC_FIELD = os.getenv('SOC_FIELD')
    SOC_ENABLE = os.getenv('SOC_ENABLE')
    PVOUTPUT_DONATION_MODE = os.getenv('PVOUTPUT_DONATION_MODE')
    PVOUTPUT_APIKEY = os.getenv("PVOUTPUT_APIKEY")
    PVOUTPUT_SYSTEMID =int(os.getenv("PVOUTPUT_SYSTEMID"))

    GOODWE_USERNAME = os.getenv('GOODWE_USERNAME')
    GOODWE_PASSWORD = os.getenv('GOODWE_PASSWORD')
    GOODWE_SYSTEMID = os.getenv('GOODWE_SYSTEMID')

    if None in [
        SOC_FIELD,
        SOC_ENABLE,
        PVOUTPUT_APIKEY,
        PVOUTPUT_DONATION_MODE,
        PVOUTPUT_SYSTEMID,

        GOODWE_PASSWORD,
        GOODWE_SYSTEMID,
        GOODWE_USERNAME,
    ] :
        print("Missing environment variable, bailing")
        return False


    if SOC_FIELD not in ADDSTATUS_PARAMETERS.keys():
        # setting an invalid field name
        print(f'Cannot log State of Charge to field "{SOC_FIELD}" - field does not exist')
        SOC_ENABLE = False

    print("Instantiating PVOutput API Object")
    pvo = PVOutput(apikey=PVOUTPUT_APIKEY,
                    systemid=PVOUTPUT_SYSTEMID,
                    donation_made=PVOUTPUT_DONATION_MODE,
                    )

    print("Connecting to Goodwe API")
    goodwe_inverter = SingleInverter(account=GOODWE_USERNAME,
                        system_id=GOODWE_SYSTEMID,
                        password=GOODWE_PASSWORD,
                        )
    # update the data
    pvdata = goodwe_inverter.getDataPvoutput()

    # add the state of charge data
    if SOC_ENABLE and PVOUTPUT_DONATION_MODE:
        pvdata[SOC_FIELD] = goodwe_inverter.get_battery_soc()
    elif SOC_ENABLE and not PVOUTPUT_DONATION_MODE:
        print("ENABLE_SOC flagged but not in donation mode, skipping.")

    # this'll throw errors if it's not right
    try:
        pvo.validate_data(pvdata, ADDSTATUS_PARAMETERS)
    except Exception as error_message: #pylint: disable=broad-except
        print(f"PVOutput.validate_data({pvdata}) failed with an error: {error_message}")
        return False

    print(f"Grabbing the PVOutput-ready data: {pvdata}")

    print(f"Called the PVOutput addstatus endpoint: {pvo.addstatus(data=pvdata).text}")
    return True

if __name__ == '__main__':
    import sys
    print("This is not a shell script")
    sys.exit(1)