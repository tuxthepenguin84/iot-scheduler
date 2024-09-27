# Modules
import argparse
from datetime import datetime
import json

# Import iot-scheduler Modules
import astral_today, iotclient as iot

### Feature Requests ###
# Front end for wife
# Edit schedule.json without rebuilding it

def main():
  arg_parser = argparse.ArgumentParser(description="IoT Schedule Builder")
  arg_parser.add_argument("-u", "--url", help="base url", default='')
  parsed_args = arg_parser.parse_args()

  # Reset Schedule
  iot.reset_all_data(parsed_args.url)

  # URL, Name [FQDN], Type [plug, bulb]
  # Scheduled Devices:
  iot.add_device(parsed_args.url, 'iot-bulb-bedroom-1.domain.com', 'bulb')
  iot.add_device(parsed_args.url, 'iot-bulb-bedroom-2.domain.com', 'bulb')
  iot.add_device(parsed_args.url, 'iot-bulb-office.domain.com', 'bulb')
  iot.add_device(parsed_args.url, 'iot-bulb-den-main.domain.com', 'bulb')
  iot.add_device(parsed_args.url, 'iot-bulb-den-corner.domain.com', 'bulb')
  iot.add_device(parsed_args.url, 'iot-plug-den-remote.domain.com', 'plug')
  iot.add_device(parsed_args.url, 'iot-bulb-nursery.domain.com', 'bulb')
  iot.add_device(parsed_args.url, 'iot-bulb-porch.domain.com', 'bulb')
  #iot.add_device(parsed_args.url, 'iot-plug-christmas-lights.domain.com', 'plug')
  #iot.add_device(parsed_args.url, 'iot-plug-christmas-tree.domain.com', 'plug')

  # Unscheduled Devices:
  iot.add_device(parsed_args.url, 'iot-plug-kettle.domain.com', 'plug')
  iot.add_device(parsed_args.url, 'iot-plug-pigarage1.domain.com', 'plug')
  iot.add_device(parsed_args.url, 'iot-plug-pimon1.domain.com', 'plug')
  iot.add_device(parsed_args.url, 'iot-plug-piwater1.domain.com', 'plug')

  # Preset Times
  dawn, sunrise, sunriseadd30, sunriseadd60, sunsetsub60, sunsetsub30, sunset, dusk = astral_today.sunupdown()
  # dawn          30 min before sunrise
  # sunrise       Sun breaks the horizon
  # sunriseadd30  30 min after sunrise
  # sunriseadd60  60 min after sunrise
  # sunsetsub60   60 min before sunset
  # sunsetsub30   30 min before sunset
  # sunset        Sun is about to disappear below the horizon
  # dusk          30 min after sunset

  altdays = ['Sun', 'Mon', 'Wed', 'Fri']
  everyday = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  samwfh = ['Mon', 'Fri']
  samsfo = ['Tue', 'Wed', 'Thu']
  weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
  weekend = ['Sun', 'Sat']

  time_format = "%H:%M"

  # URL, DeviceID [index of above], DoW [Sun, Mon, Tue, Wed, Thu, Fri, Sat or preset], Time [24hr or preset], Power
  #
  # Add Schedule:
  # iot-bulb-bedroom-1
  iot.add_schedule(parsed_args.url, 1, everyday, sunriseadd60, 'off')
  iot.add_schedule(parsed_args.url, 1, everyday, sunsetsub30, 'on')
  iot.add_schedule(parsed_args.url, 1, everyday, '22:00', 'off')
  # iot-bulb-bedroom-sam
  iot.add_schedule(parsed_args.url, 2, everyday, sunriseadd60, 'off')
  iot.add_schedule(parsed_args.url, 2, everyday, sunsetsub30, 'on')
  iot.add_schedule(parsed_args.url, 2, everyday, '22:00', 'off')
  # iot-bulb-office
  iot.add_schedule(parsed_args.url, 3, weekdays, '05:50', 'on')
  iot.add_schedule(parsed_args.url, 3, samsfo, '06:20', 'off')
  iot.add_schedule(parsed_args.url, 3, everyday, sunriseadd60, 'off')
  iot.add_schedule(parsed_args.url, 3, everyday, sunsetsub30, 'on')
  iot.add_schedule(parsed_args.url, 3, everyday, '20:00', 'off')
  iot.add_schedule(parsed_args.url, 3, everyday, '00:00', 'off')
  # iot-bulb-den-main
  iot.add_schedule(parsed_args.url, 4, everyday, sunset, 'on')
  iot.add_schedule(parsed_args.url, 4, everyday, '22:00', 'off')
  iot.add_schedule(parsed_args.url, 4, everyday, '00:00', 'off')
  # iot-bulb-den-corner
  iot.add_schedule(parsed_args.url, 5, everyday, sunset, 'on')
  iot.add_schedule(parsed_args.url, 5, everyday, '22:00', 'off')
  iot.add_schedule(parsed_args.url, 5, everyday, '00:00', 'off')
  # iot-plug-den-remote
  iot.add_schedule(parsed_args.url, 6, altdays, '06:00', 'on')
  iot.add_schedule(parsed_args.url, 6, altdays, '09:00', 'off')
  # iot-bulb-nursery
  iot.add_schedule(parsed_args.url, 7, everyday, sunriseadd60, 'off')
  if datetime.strptime(sunsetsub30, time_format).time() < datetime.strptime('18:15', time_format).time():
    iot.add_schedule(parsed_args.url, 7, everyday, sunsetsub30, 'on')
  iot.add_schedule(parsed_args.url, 7, everyday, '18:15', 'off')
  # iot-bulb-porch
  iot.add_schedule(parsed_args.url, 8, everyday, '06:00', 'on')
  iot.add_schedule(parsed_args.url, 8, everyday, sunriseadd30, 'off')
  iot.add_schedule(parsed_args.url, 8, everyday, sunset, 'on')
  iot.add_schedule(parsed_args.url, 8, everyday, '21:00', 'off')
  # iot-plug-christmas-lights
  #iot.add_schedule(parsed_args.url, 9, everyday, sunset, 'on')
  #iot.add_schedule(parsed_args.url, 9, everyday, sunrise, 'off')
  # iot-plug-christmas-tree
  #iot.add_schedule(parsed_args.url, 10, everyday, sunsetsub30, 'on')
  #iot.add_schedule(parsed_args.url, 10, everyday, '20:00', 'off')

  # Print Schedules & Devices
  print(json.dumps(iot.get_all_schedules(parsed_args.url).json(), indent=2))
  print(json.dumps(iot.get_all_devices(parsed_args.url).json(), indent=2))

if __name__ == "__main__":
  main()
