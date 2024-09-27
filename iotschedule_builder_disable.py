# Modules
import argparse

# Import iot-scheduler Modules
import iotclient as iot

### Feature Requests ###
# Front end for wife
# Edit schedule.json without rebuilding it

def main():
    arg_parser = argparse.ArgumentParser(description="IoT Schedule Builder")
    arg_parser.add_argument("-u", "--url", help="base url", default='')
    parsed_args = arg_parser.parse_args()

    # Reset Schedule
    iot.resetAllData(parsed_args.url)

    # URL, Name [FQDN], Type [plug, bulb, etc.]
    iot.addDevice(parsed_args.url, 'iot-bulb-bedroom-1.domain.io', 'bulb')
    iot.addDevice(parsed_args.url, 'iot-bulb-bedroom-2.domain.io', 'bulb')
    iot.addDevice(parsed_args.url, 'iot-bulb-office.domain.io', 'bulb')
    iot.addDevice(parsed_args.url, 'iot-bulb-den-main.domain.io', 'bulb')
    iot.addDevice(parsed_args.url, 'iot-bulb-den-corner.domain.io', 'bulb')
    iot.addDevice(parsed_args.url, 'iot-bulb-nursery.domain.io', 'bulb')
    iot.addDevice(parsed_args.url, 'iot-bulb-porch.domain.io', 'bulb')
    #iot.addDevice(parsed_args.url, 'iot-plug-christmas-lights.domain.io', 'plug')
    #iot.addDevice(parsed_args.url, 'iot-plug-christmas-tree.domain.io', 'plug')
    iot.addDevice(parsed_args.url, 'iot-plug-kettle.domain.io', 'plug')
    iot.addDevice(parsed_args.url, 'iot-plug-nursery-noise.domain.io', 'plug')
    iot.addDevice(parsed_args.url, 'iot-plug-pigarage1.domain.io', 'plug')
    iot.addDevice(parsed_args.url, 'iot-plug-pimon1.domain.io', 'plug')
    iot.addDevice(parsed_args.url, 'iot-plug-piwater1.domain.io', 'plug')

if __name__ == "__main__":
    main()
