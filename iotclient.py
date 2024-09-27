# Modules
from datetime import datetime
import json
import os
import requests
import sys

def get_all_devices(base_url):
  return requests.get(base_url + 'devicegetall')

def get_device_id(base_url):
  device_latest_id = requests.get(base_url + 'devicegetid')
  return device_latest_id.json()

def get_device(base_url, device_id):
  return requests.get(base_url + 'devicebuilder/' + str(device_id))

def add_device(base_url, device_name, device_type):
  new_device_data = {
    'devicename': device_name,
    'devicetype': device_type
  }
  return requests.put(base_url + 'devicebuilder/' + str(get_device_id(base_url)), data=new_device_data)

def update_device(base_url, device_id, device_name):
  updated_device_data = {
    'devicename': device_name
  }
  return requests.patch(base_url + 'devicebuilder/' + str(device_id), data=updated_device_data)

def delete_device(base_url, device_id):
  return requests.delete(base_url + 'devicebuilder/' + str(device_id))

def get_all_schedules(base_url):
  return requests.get(base_url + 'schedulegetall')

def get_schedule_id(base_url):
  response = requests.get(base_url + 'schedulegetid')
  return response.json()

def get_schedule(base_url, schedule_id):
  return requests.get(base_url + 'schedulebuilder/' + str(schedule_id))

def add_schedule(base_url, device_id, dow, time, power):
  if type(dow) is list:
    for day in dow:
      add_schedule(base_url, device_id, day, time, power)
  else:
    add_schedule_data = {
      'deviceid': device_id,
      'dow': dow,
      'time': time,
      'power': power,
    }
    return requests.put(base_url + 'schedulebuilder/' + str(get_schedule_id(base_url)), data=add_schedule_data)

def update_schedule(base_url, schedule_id, dow, time, power):
  if type(dow) is list:
    for day in dow:
      update_schedule(base_url, schedule_id, day, time, power)
  else:
    updated_schedule_data = {
      'dow': dow,
      'time': time,
      'power': power,
    }
    return requests.patch(base_url + 'schedulebuilder/' + str(schedule_id), data=updated_schedule_data)

def delete_schedule(base_url, schedule_id):
  return requests.delete(base_url + 'schedulebuilder/' + str(schedule_id))

def run_schedule(base_url, device_id, requested_power):
  new_device_state = {
    'requestedpower': requested_power
  }
  return requests.put(base_url + 'runschedule/' + str(device_id), data=new_device_state)

def get_power(base_url, device_name):
  device_state = {
    'devicename': device_name,
  }
  return requests.get(base_url + 'power', data=device_state)

def update_power(base_url, device_name, requested_power):
  new_device_state = {
    'devicename': device_name,
    'requestedpower': requested_power
  }
  return requests.put(base_url + 'power', data=new_device_state)

def get_brightness(base_url, device_name):
  device_state = {
    'devicename': device_name
  }
  return requests.get(base_url + 'brightness', data=device_state)

def update_brightness(base_url, device_name, requested_brightness):
  new_device_state = {
    'devicename': device_name,
    'requestedbrightness': requested_brightness
  }
  return requests.put(base_url + 'brightness', data=new_device_state)

def get_temperature(base_url, device_name):
  device_state = {
    'devicename': device_name
  }
  return requests.get(base_url + 'temperature', data=device_state)

def update_temperature(base_url, device_name, requested_temperature):
  new_device_state = {
    'devicename': device_name,
    'requestedtemperature': requested_temperature
  }
  return requests.put(base_url + 'temperature', data=new_device_state)

def get_hsv(base_url, device_name):
  device_state = {
    'devicename': device_name
  }
  return requests.get(base_url + 'hsv', data=device_state)

def update_hsv(base_url, device_name, requested_hue, requested_saturation, requested_value):
  new_device_state = {
    'devicename': device_name,
    'requestedhue': requested_hue,
    'requestedsaturation': requested_saturation,
    'requestedvalue': requested_value
  }
  return requests.put(base_url + 'hsv', data=new_device_state)

def reset_all_data(base_url):
  return requests.delete(base_url + 'resetall')

def unit_testing(base_url, mode, file_name):
  unit_testing_data = {
    'filename': file_name
  }
  return requests.put(base_url + 'unittesting/' + str(mode), data=unit_testing_data)

# Schedule Functions
def import_schedule(schedule_file, time_format):
  schedule_json_data = dutils.load_json_file(schedule_file)
  if schedule_json_data is None:
    schedule_json_data = reset_schedule(time_format)
  return schedule_json_data

def reset_schedule(time_format, default_brightness = 20, default_temperature = 3000):
  json_data = {# move this to default.json
                "created": datetime.now().strftime(time_format),
                "edited": datetime.now().strftime(time_format),
                "defaults":{
                  "brightness": default_brightness,
                  "temperature": default_temperature
                },
                "devices":{},
                "schedules_edited": datetime.now().strftime(time_format),
                "schedules":{}
              }
  return json_data

def write_schedule(json_data, schedule_file, time_format):
  json_data['edited'] = datetime.now().strftime(time_format)
  f = open(schedule_file,"w")
  f.write(json.dumps(json_data, indent=2))
  f.close()
