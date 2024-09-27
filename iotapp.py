# Modules
import argparse
from datetime import datetime
import sys
from tabulate import tabulate

# Import iot-scheduler Modules
import iotclient as iot

def get_todays_schedule(url):
  DoW = datetime.now().strftime("%a")

  all_schedules = iot.get_all_schedules(url).json()
  all_devices = iot.get_all_devices(url).json()
  todays_schedule = {"device_name":[],"power":[],"time":[]};
  for schedule in all_schedules:
    if DoW in all_schedules[schedule]['dow']:
      device_id = all_schedules[schedule]['deviceid']
      todays_schedule["device_name"].append(all_devices[device_id]['devicename'].replace(".delchamps.io",""))
      todays_schedule["power"].append(all_schedules[schedule]['power'].upper())
      todays_schedule["time"].append(datetime.strptime(all_schedules[schedule]['time'], "%H:%M").strftime("%-I:%M %p"))
  return todays_schedule

def get_device_power_status(url):
  all_devices = iot.get_all_devices(url).json()
  power_status = {"device_name":[],"power":[]};
  for device_id in all_devices:
    device_name = all_devices[device_id]['devicename']
    power_status["device_name"].append(device_name.replace(".delchamps.io",""))
    power_status["power"].append(iot.get_power(url, device_name).text.replace("\"","").upper())
  return power_status

def main():
  brightness = {
    "dim": 20,
    "mid": 50,
    "bright": 100,
    "default": 20
  }

  temperature = {
    "warm": 3000,
    "sunlight": 4800,
    "cool": 6500,
    "default": 3000
  }

  hue = {
    "red": 0,
    "orange": 10,
    "yellow": 40,
    "green": 120,
    "aqua": 180,
    "blue": 240,
    "purple": 300
  }

  if (parsed_power or parsed_brightness or parsed_temperature or parsed_hsv) and (not parsed_device and not parsed_group):
    print('Must specify device hostname')
    sys.exit(1)
  elif (not parsed_power and not parsed_brightness and not parsed_temperature and not parsed_hsv) and parsed_device:
    print('Must specify power, brightness, temperature or hsv')
    sys.exit(1)

  if parsed_schedule:
    print(f'\nToday\'s Schedule')
    print(tabulate(get_todays_schedule(parsed_url), headers=["Device","Power", "Time"], tablefmt="presto", colalign=("left","left","right")))

  if parsed_status:
    print(f'\nDevice Power Status')
    print(tabulate(get_device_power_status(parsed_url), headers=["Device","Power"], tablefmt="presto", colalign=("left","left")))

  if parsed_power:
    if parsed_device == 'all':
      all_devices = iot.get_all_devices(parsed_url).json()
      for device_id in all_devices:
        device_name = all_devices[device_id]['devicename']
        response = iot.update_power(parsed_url, device_name, parsed_power)
        print(response.text.strip().replace("\"","").upper())
    elif parsed_device == None and parsed_group != None:
      for device_name in groups[parsed_group]:
        response = iot.update_power(parsed_url, device_name, parsed_power)
        print(response.text.strip().replace("\"","").upper())
    else:
      response = iot.update_power(parsed_url, parsed_device, parsed_power)
      print(response.text.strip().replace("\"","").upper())

  if parsed_brightness:
    if parsed_device == 'all':
      all_devices = iot.get_all_devices(parsed_url).json()
      for device_id in all_devices:
        if all_devices[device_id]['devicetype'] == 'bulb':
          device_name = all_devices[device_id]['devicename']
          print(iot.update_brightness(parsed_url, device_name, brightness[parsed_brightness]).text.strip())
    else:
      print(iot.update_brightness(parsed_url, parsed_device, brightness[parsed_brightness]).text.strip())

  if parsed_temperature:
    if parsed_device == 'all':
      all_devices = iot.get_all_devices(parsed_url).json()
      for device_id in all_devices:
        if all_devices[device_id]['devicetype'] == 'bulb':
          device_name = all_devices[device_id]['devicename']
          print(iot.update_temperature(parsed_url, device_name, temperature[parsed_temperature]).text.strip())
    else:
      print(iot.update_temperature(parsed_url, parsed_device, temperature[parsed_temperature]).text.strip())

  if parsed_hsv:
    if parsed_device == 'all':
      all_devices = iot.get_all_devices(parsed_url).json()
      for device_id in all_devices:
        if all_devices[device_id]['devicetype'] == 'bulb':
          device_name = all_devices[device_id]['devicename']
          print(iot.update_hsv(parsed_url, device_name, hue[parsed_hsv], 100, 100).text.strip())
    else:
      print(iot.update_hsv(parsed_url, parsed_device, hue[parsed_hsv], 100, 100).text.strip())

if __name__ == "__main__":
  # Arg Parser
  arg_parser = argparse.ArgumentParser(description="IoT App")
  arg_parser.add_argument("-u", "--url", help="Base URL", default='')
  arg_parser.add_argument("-t", "--status", help="Device Power Status", action='store_true', default=False)
  arg_parser.add_argument("-s", "--schedule", help="Todays Schedule", action='store_true', default=False)
  arg_parser.add_argument("-p", "--power", help="Power On/Off", choices=['on', 'off'])
  arg_parser.add_argument("-b", "--brightness", help="Brightness (0-100) or default")
  arg_parser.add_argument("-k", "--temperature", help="Temperature (Kelvin) (2500-6500) or default")
  arg_parser.add_argument("-c", "--hsv", help="red, orange, yellow, green, aqua, blue, purple", choices=['red', 'orange', 'yellow', 'green', 'aqua', 'blue', 'purple'])
  arg_parser.add_argument("-d", "--device", help="Device hostname, fqdn, all")
  arg_parser.add_argument("-g", "--group", help="den, bedroom")
  parsed_args = arg_parser.parse_args()
  parsed_brightness = parsed_args.brightness
  parsed_device = parsed_args.device
  parsed_group = parsed_args.group
  parsed_hsv = parsed_args.hsv
  parsed_power = parsed_args.power
  parsed_schedule = parsed_args.schedule
  parsed_status = parsed_args.status
  parsed_temperature = parsed_args.temperature
  parsed_url = parsed_args.url

  groups = {
    'backrooms': [
      'iot-bulb-bedroom-1',
      'iot-bulb-bedroom-2',
      'iot-bulb-nursery',
      'iot-bulb-office'
    ],
    'bedroom': [
      'iot-bulb-bedroom-1',
      'iot-bulb-bedroom-2'
    ],
    'den': [
      'iot-bulb-den-main',
      'iot-bulb-den-corner'
    ],
    'house': [
      'iot-bulb-bedroom-1',
      'iot-bulb-bedroom-2',
      'iot-bulb-nursery',
      'iot-bulb-office',
      'iot-bulb-porch'
    ]
  }

  # Call Main Function
  main()
