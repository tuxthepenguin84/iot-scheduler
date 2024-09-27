# Modules
import asyncio
from datetime import datetime
from flask import Flask
from flask_cors import CORS
from flask_restful import abort, Api, reqparse, Resource
import json
import kasa
import os
import sys

# Import iot-scheduler Modules
import iotclient as iot

# Functions
def get_device_names(device_name):
  if device_name.endswith('.delchamps.io'):
    return device_name.replace(".delchamps.io",""), device_name
  else:
    return device_name, device_name + '.delchamps.io'

def message_out(message):
  if unit_testing_mode == False and matrix_enabled:
    dmessage.send_matrix_message(message, matrix_room_id, matrix_token)
  message = f'{datetime.now().strftime(time_format)} | {message}'
  print(message)

# Check Functions
def check_existing_device_id(device_id, schedule_json):
  if device_id not in schedule_json['devices']:
    abort(404, message='Could not find device_id')

def check_not_existing_device_id(device_id, schedule_json):
  if device_id in schedule_json['devices']:
    abort(409, message='device_id already exists')

def check_existing_schedule_id(schedule_id, schedule_json):
  if schedule_id not in schedule_json['schedules']:
    abort(404, message='Could not find schedule_id')

def check_not_existing_schedule(new_schedule_data, schedule_id, schedule_json):
  if schedule_id in schedule_json['schedules']:
    abort(409, message='schedule_id already exists')
  for schedule in schedule_json['schedules']:
    if new_schedule_data['deviceid'] == schedule_json['schedules'][schedule]['deviceid'] and new_schedule_data['dow'] == schedule_json['schedules'][schedule]['dow'] and new_schedule_data['time'] == schedule_json['schedules'][schedule]['time']:
      abort(409, message='schedule already exists')

# Device Functions
def get_device_id(schedule_json, device_name):
  for each_device in schedule_json['devices']:
    if schedule_json['devices'][each_device]['devicename'] == device_name:
      device_id = each_device
      return device_id
  abort(404, message='Unknown devicename')

# Power Functions
def get_power(schedule_json, device_id):
  check_existing_device_id(device_id, schedule_json)
  device_name = schedule_json['devices'][device_id]['devicename']
  device_type = schedule_json['devices'][device_id]['devicetype']
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  elif device_type == 'plug':
    this_device = kasa.SmartPlug(device_name)
  else:
    abort(404, message='Unknown device type')
  try:
    asyncio.run(this_device.update())
  except:
    schedule_json['devices'][device_id]['currentpower'] = 'n/a'
    iot.write_schedule(schedule_json, schedule_file, time_format)
    return schedule_json['devices'][device_id]['currentpower']
  if this_device.is_on:
    schedule_json['devices'][device_id]['currentpower'] = 'on'
  elif not this_device.is_on:
    schedule_json['devices'][device_id]['currentpower'] = 'off'
  iot.write_schedule(schedule_json, schedule_file, time_format)
  return schedule_json['devices'][device_id]['currentpower']

async def update_kasa_device_power(device_name, device_type, requested_power):
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  elif device_type == 'plug':
    this_device = kasa.SmartPlug(device_name)
  else:
    abort(404, message='Unknown device type')
  await this_device.update()
  if requested_power == 'on':
    await this_device.turn_on(transition=transition_time)
    await this_device.update()
  elif requested_power == 'off':
    await this_device.turn_off(transition=transition_time)
    await this_device.update()
  else:
    abort(404, message='Unknown requested power state')

# Brightness Functions
def get_brightness(schedule_json, device_id):
  check_existing_device_id(device_id, schedule_json)
  device_name = schedule_json['devices'][device_id]['devicename']
  device_type = schedule_json['devices'][device_id]['devicetype']
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  else:
    abort(409, message='Only bulbs support brightness')
  try:
    asyncio.run(this_device.update())
  except:
    abort(404, message='Unknown name or service')
  return this_device.brightness

async def update_kasa_device_brightness(device_name, device_type, requested_brightness):
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  else:
    abort(409, message='Only bulbs support brightness')
  if requested_brightness <= 100 and requested_brightness >= 0:
    await this_device.update()
    await this_device.set_brightness(requested_brightness, transition=transition_time)
  else:
    abort(409, message='Brightness must be between 0-100')

# Temperature
def get_temperature(schedule_json, device_id):
  check_existing_device_id(device_id, schedule_json)
  device_name = schedule_json['devices'][device_id]['devicename']
  device_type = schedule_json['devices'][device_id]['devicetype']
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  else:
    abort(409, message='Only bulbs support Temperature')
  try:
    asyncio.run(this_device.update())
  except:
    abort(404, message='Unknown name or service')
  return this_device.color_temp

async def update_kasa_device_temperature(device_name, device_type, requested_temperature):
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  else:
    abort(409, message='Only bulbs support Temperature')
  if requested_temperature <= 6500 and requested_temperature >= 2500:
    await this_device.update()
    await this_device.set_color_temp(requested_temperature, transition=transition_time)
  else:
    abort(409, message='Temperature must be between 2500-6500')

# HSV
def get_hsv(schedule_json, device_id):
  check_existing_device_id(device_id, schedule_json)
  device_name = schedule_json['devices'][device_id]['devicename']
  device_type = schedule_json['devices'][device_id]['devicetype']
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  else:
    abort(409, message='Only bulbs support HSV')
  try:
    asyncio.run(this_device.update())
  except:
    abort(404, message='Unknown name or service')
  return this_device.hsv

async def update_kasa_device_hsv(device_name, device_type, requested_hue, requested_saturation, requested_value):
  if device_type == 'bulb':
    this_device = kasa.SmartBulb(device_name)
  else:
    abort(409, message='Only bulbs support HSV')
  if requested_hue < 360 and requested_hue >= 0 and requested_saturation <= 100 and requested_saturation >= 0 and requested_value <= 100 and requested_value >= 0:
    await this_device.update()
    await this_device.set_hsv(requested_hue, requested_saturation, requested_value, transition=transition_time)
  else:
    abort(409, message='Hue must be between 0-360, saturation must be between 0-100, and value must be between 0-100')

# Classes
class DeviceBuilder(Resource):
  def get(self, device_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_device_id(device_id, schedule_json)
    return schedule_json['devices'][device_id], 200

  def put(self, device_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_not_existing_device_id(device_id, schedule_json)
    schedule_json['devices'][device_id] = device_put_args.parse_args()
    schedule_json['devices'][device_id]['currentpower'] = get_power(schedule_json, device_id)
    iot.write_schedule(schedule_json, schedule_file, time_format)
    return schedule_json['devices'][device_id], 201

  def patch(self, device_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_device_id(device_id, schedule_json)
    device_name = device_patch_args.parse_args()['devicename']
    _, device_name_fqdn = get_device_names(device_name)
    if device_name_fqdn != None and device_name_fqdn != '' and schedule_json['devices'][device_id]['devicename'] != device_name_fqdn:
      schedule_json['devices'][device_id]['devicename'] = device_name_fqdn
      iot.write_schedule(schedule_json, schedule_file, time_format)
      return schedule_json['devices'][device_id], 201
    else:
      return schedule_json['devices'][device_id], 400

  def delete(self, device_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_device_id(device_id, schedule_json)
    del schedule_json['devices'][device_id]
    for device in schedule_json['schedules'].copy():
      if schedule_json['schedules'][device]['deviceid'] == device_id:
        del schedule_json['schedules'][device]
    iot.write_schedule(schedule_json, schedule_file, time_format)
    return '', 204

class DeviceGetAll(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    if len(schedule_json['devices']) > 0:
      return (schedule_json['devices'], 200)
    else:
      return 'No devices in schedule', 404

class DeviceGetID(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    return len(schedule_json['devices']) + 1, 200

class ScheduleBuilder(Resource):
  def get(self, schedule_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_schedule_id(schedule_id, schedule_json)
    return schedule_json['schedules'][schedule_id], 200

  def put(self, schedule_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_device_id(schedule_put_args.parse_args()['deviceid'], schedule_json)
    check_not_existing_schedule(schedule_put_args.parse_args(), schedule_id, schedule_json)
    schedule_json['schedules'][schedule_id] = schedule_put_args.parse_args()
    schedule_json['schedules_edited'] = datetime.now().strftime("%a %m/%d %H:%M")
    iot.write_schedule(schedule_json, schedule_file, time_format)
    return schedule_json['schedules'][schedule_id], 201

  def patch(self, schedule_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_schedule_id(schedule_id, schedule_json)
    schedulesChanged = False
    if schedule_patch_args.parse_args()['dow'] != None and schedule_patch_args.parse_args()['dow'] != '' and schedule_json['schedules'][schedule_id]['dow'] != schedule_patch_args.parse_args()['dow']:
      schedule_json['schedules'][schedule_id]['dow'] = schedule_patch_args.parse_args()['dow']
      schedulesChanged = True
    if schedule_patch_args.parse_args()['time'] != None and schedule_patch_args.parse_args()['time'] != '' and schedule_json['schedules'][schedule_id]['time'] != schedule_patch_args.parse_args()['time']:
      schedule_json['schedules'][schedule_id]['time'] = schedule_patch_args.parse_args()['time']
      schedulesChanged = True
    if schedule_patch_args.parse_args()['power'] != None and schedule_patch_args.parse_args()['power'] != '' and schedule_json['schedules'][schedule_id]['power'] != schedule_patch_args.parse_args()['power']:
      schedule_json['schedules'][schedule_id]['power'] = schedule_patch_args.parse_args()['power']
      schedulesChanged = True
    if schedulesChanged:
      schedule_json['schedules_edited'] = datetime.now().strftime("%a %m/%d %H:%M")
      iot.write_schedule(schedule_json, schedule_file, time_format)
      return schedule_json['schedules'][schedule_id], 201
    else:
      return schedule_json['schedules'][schedule_id], 400

  def delete(self, schedule_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    check_existing_schedule_id(schedule_id, schedule_json)
    del schedule_json['schedules'][schedule_id]
    schedule_json['schedules_edited'] = datetime.now().strftime("%a %m/%d %H:%M")
    iot.write_schedule(schedule_json, schedule_file, time_format)
    return '', 204

class ScheduleGetAll(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    if len(schedule_json['schedules']) > 0:
      return (schedule_json['schedules'], 200)
    elif len(schedule_json['schedules']) == 0:
      return ('', 404)

class ScheduleGetID(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    return len(schedule_json['schedules']) + 1, 200

class RunSchedule(Resource):
  def put(self, device_id):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = schedule_json['devices'][device_id]['devicename']
    device_type = schedule_json['devices'][device_id]['devicetype']
    device_name_host, device_name_fqdn = get_device_names(device_name)
    requested_power = run_schedule_put_args.parse_args()['requestedpower']
    current_power = get_power(schedule_json, device_id)
    if device_type != 'bulb' and device_type != 'plug':
      return "Unknown device type", 404
    if requested_power == current_power:
      return "Device already in requested state", 200
    if unit_testing_mode == False:
      if device_type == 'bulb':
        asyncio.run(update_kasa_device_brightness(device_name_fqdn, device_type, default_brightness))
        asyncio.run(update_kasa_device_temperature(device_name_fqdn, device_type, default_temperature))
      asyncio.run(update_kasa_device_power(device_name_fqdn, device_type, requested_power))
      message = f'{device_name_host} | SCHEDULE | POWER {requested_power}'
      message_out(message)
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          device_name_host,
          requested_power,
          True,
          "power"
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
    current_power = get_power(schedule_json, device_id)
    return current_power, 200

class Power(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = power_get_args.parse_args()['devicename']
    _, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    current_power = get_power(schedule_json, device_id)
    return current_power, 200

  def put(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = power_put_args.parse_args()['devicename']
    device_name_host, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    device_type = schedule_json['devices'][device_id]['devicetype']
    requested_power = power_put_args.parse_args()['requestedpower']
    current_power = get_power(schedule_json, device_id)
    if device_type != 'bulb' and device_type != 'plug':
      return "Unknown device type", 404
    if requested_power == current_power:
      return "Device already in requested state", 409
    if unit_testing_mode == False:
      asyncio.run(update_kasa_device_power(device_name_fqdn, device_type, requested_power))
      message = f'{device_name_host} | POWER {requested_power}'
      message_out(message)
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          device_name_host,
          requested_power,
          False,
          "power"
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
    current_power = get_power(schedule_json, device_id)
    return current_power, 200

class Brightness(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = brightness_get_args.parse_args()['devicename']
    _, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    current_brightness = get_brightness(schedule_json, device_id)
    return current_brightness, 200

  def put(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = brightness_put_args.parse_args()['devicename']
    device_name_host, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    device_type = schedule_json['devices'][device_id]['devicetype']
    requested_brightness = brightness_put_args.parse_args()['requestedbrightness']
    if unit_testing_mode == False:
      asyncio.run(update_kasa_device_brightness(device_name_fqdn, device_type, requested_brightness))
      message = f'{device_name_host} | BRIGHT {requested_brightness}'
      message_out(message)
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          device_name_host,
          requested_brightness,
          False,
          "brightness"
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
    current_brightness = get_brightness(schedule_json, device_id)
    get_power(schedule_json, device_id)
    return current_brightness, 200

class Temperature(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = temperature_get_args.parse_args()['devicename']
    _, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    current_temperature = get_temperature(schedule_json, device_id)
    return current_temperature, 200

  def put(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = temperature_put_args.parse_args()['devicename']
    device_name_host, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    device_type = schedule_json['devices'][device_id]['devicetype']
    requested_temperature = temperature_put_args.parse_args()['requestedtemperature']
    if unit_testing_mode == False:
      asyncio.run(update_kasa_device_temperature(device_name_fqdn, device_type, requested_temperature))
      message = f'{device_name_host} | TEMP {requested_temperature}'
      message_out(message)
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          device_name_host,
          requested_temperature,
          False,
          "temperature"
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
    current_temperature = get_temperature(schedule_json, device_id)
    get_power(schedule_json, device_id)
    return current_temperature, 200

class HSV(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = hsv_get_args.parse_args()['devicename']
    _, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    current_hsv = get_hsv(schedule_json, device_id)
    return current_hsv, 200

  def put(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    device_name = hsv_put_args.parse_args()['devicename']
    device_name_host, device_name_fqdn = get_device_names(device_name)
    device_id = get_device_id(schedule_json, device_name_fqdn)
    device_type = schedule_json['devices'][device_id]['devicetype']
    requested_hue = hsv_put_args.parse_args()['requested_hue']
    requested_saturation = hsv_put_args.parse_args()['requested_saturation']
    requested_value = hsv_put_args.parse_args()['requested_value']
    if unit_testing_mode == False:
      asyncio.run(update_kasa_device_hsv(device_name_fqdn, device_type, requested_hue, requested_saturation, requested_value))
      message = f'{device_name_host} | HSV {requested_hue} {requested_saturation} {requested_value}'
      message_out(message)
      if db_enabled:
        db_values = (
          datetime.now().strftime(date_only),
          datetime.now().strftime(time_only),
          device_name_host,
          f'{requested_hue} {requested_saturation} {requested_value}',
          False,
          "hsv"
        )
        ddatabase.insert_into_db(db_connection_info, db_table, db_columns, db_values)
    current_hsv = get_hsv(schedule_json, device_id)
    get_power(schedule_json, device_id)
    return current_hsv, 200

class Status(Resource):
  def get(self):
    return 'ready', 200

class Health(Resource):
  def get(self):
    return 'up', 200

class ResetAll(Resource):
  def delete(self):
    schedule_json = iot.reset_schedule(time_format)
    iot.write_schedule(schedule_json, schedule_file, time_format)
    return '', 204

class Metrics(Resource):
  def get(self):
    schedule_json = iot.import_schedule(schedule_file, time_format)
    return 'Coming soon', 200

class UnitTesting(Resource):
  def put(self, mode):
    global unit_testing_mode
    global schedule_file
    if int(mode) == 1:
      unit_testing_mode = True
      schedule_file = unit_testing_put_args.parse_args()['filename']
      return 'On', 200
    elif int(mode) == 0:
      unit_testing_mode = False
      schedule_file = original_schedule_file
      os.remove(unit_testing_put_args.parse_args()['filename'])
      return 'Off', 200

def main():
  # Flask
  app = Flask(__name__)
  CORS(app)
  api = Api(app)
  api.add_resource(DeviceBuilder, "/devicebuilder/<device_id>")
  api.add_resource(DeviceGetAll, "/devicegetall")
  api.add_resource(DeviceGetID, "/devicegetid")
  api.add_resource(ScheduleBuilder, "/schedulebuilder/<schedule_id>")
  api.add_resource(ScheduleGetAll, "/schedulegetall")
  api.add_resource(ScheduleGetID, "/schedulegetid")
  api.add_resource(RunSchedule, "/runschedule/<device_id>")
  api.add_resource(Power, "/power")
  api.add_resource(Brightness, "/brightness")
  api.add_resource(Temperature, "/temperature")
  api.add_resource(HSV, "/hsv")
  api.add_resource(Status, "/status")
  api.add_resource(Health, "/health")
  api.add_resource(ResetAll, "/resetall")
  api.add_resource(Metrics, "/metrics")
  api.add_resource(UnitTesting, "/unittesting/<mode>")
  app.run(host='0.0.0.0', port=5000)
  app.run(debug=True)
  #ssl_context='adhoc'

if __name__ == "__main__":
  # Variables
  date_only = "%m/%d/%Y"
  time_format = "%a %m/%d %H:%M"
  time_only = "%H:%M:%S"
  unit_testing_mode = False

  # Bulb Variables
  default_brightness = 20
  default_temperature = 3000
  transition_time = 500

  # Request Parser
  device_put_args = reqparse.RequestParser()
  device_put_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  device_put_args.add_argument('devicetype', type=str, help="Type of device", location='form', case_sensitive=False, required=True)
  device_patch_args = reqparse.RequestParser()
  device_patch_args.add_argument('devicename', type=str, help="Name of device", case_sensitive=False, location='form')
  device_patch_args.add_argument('devicetype', type=str, help="Type of device", case_sensitive=False, location='form')
  schedule_put_args = reqparse.RequestParser()
  schedule_put_args.add_argument('deviceid', type=str, help="Device ID", location='form', required=True)
  schedule_put_args.add_argument('dow', type=str, help="Day of Week to run device", location='form', required=True)
  schedule_put_args.add_argument('time', type=str, help="Time of day to start device", location='form', required=True)
  schedule_put_args.add_argument('power', type=str, help="On/Off", location='form', case_sensitive=False, required=True)
  schedule_patch_args = reqparse.RequestParser()
  schedule_patch_args.add_argument('dow', type=str, help="Day of Week to run device", location='form')
  schedule_patch_args.add_argument('time', type=str, help="Time of day to start device", location='form')
  schedule_patch_args.add_argument('power', type=str, help="On/Off", case_sensitive=False, location='form')
  run_schedule_put_args = reqparse.RequestParser()
  run_schedule_put_args.add_argument('requestedpower', type=str, help="On/Off", location='form', case_sensitive=False, required=True)
  power_get_args = reqparse.RequestParser()
  power_get_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  power_put_args = reqparse.RequestParser()
  power_put_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  power_put_args.add_argument('requestedpower', type=str, help="On/Off", location='form', case_sensitive=False, required=True)
  brightness_get_args = reqparse.RequestParser()
  brightness_get_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  brightness_put_args = reqparse.RequestParser()
  brightness_put_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  brightness_put_args.add_argument('requestedbrightness', type=int, help="0-100", location='form', required=True)
  temperature_get_args = reqparse.RequestParser()
  temperature_get_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  temperature_put_args = reqparse.RequestParser()
  temperature_put_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  temperature_put_args.add_argument('requestedtemperature', type=int, help="2500-6500", location='form', required=True)
  hsv_get_args = reqparse.RequestParser()
  hsv_get_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  hsv_put_args = reqparse.RequestParser()
  hsv_put_args.add_argument('devicename', type=str, help="Name of device", location='form', case_sensitive=False, required=True)
  hsv_put_args.add_argument('requested_hue', type=int, help="0-359", location='form', required=True)
  hsv_put_args.add_argument('requested_saturation', type=int, help="0-100", location='form', required=True)
  hsv_put_args.add_argument('requested_value', type=int, help="0-100", location='form', required=True)
  unit_testing_put_args = reqparse.RequestParser()
  unit_testing_put_args.add_argument('filename', type=str, help="Name of unit testing json file", location='form', required=True)

  # Import params.json Data
  params_file = os.path.join(script_dir, 'params.json')
  params_json = dutils.load_json_file(params_file)
  if params_json is None:
    print(f'Unable to import {params_file} data')
    sys.exit(1)

  # Import Database Connection Data
  if 'database' in params_json:
    db_enabled = True
    db_json = params_json['database']
    db_columns = db_json['columns']
    db_connection_info = db_json['connection']
    db_retries = db_json['retries']
    db_table = db_json['table']
  else:
    db_enabled = False
    db_columns = None
    db_connection_info = None
    db_retries = None
    db_table = None

  # Import Matrix Data
  if 'matrix' in params_json:
    matrix_enabled = True
    matrix_json = params_json['matrix']
    matrix_room_id = matrix_json['roomid']
    matrix_token = matrix_json['token']
  else:
    matrix_enabled = False
    matrix_room_id = None
    matrix_token = None

  # Import Schedule Data
  original_schedule_file = schedule_file = os.path.join(script_dir, 'schedule.json')
  schedule_json = iot.import_schedule(schedule_file, time_format)
  if schedule_json is None:
    print('Unable to import schedule data')
    sys.exit(1)
  print(json.dumps(schedule_json, indent=2))

  # Startup
  startup = {
    'SCHEDULE': schedule_file,
    'DB_COLUMNS': db_columns,
    'DB_CONN_INFO': db_connection_info,
    'DB_RETRIES': db_retries,
    'DB_TABLE': db_table,
    'MATRIXROOMID': matrix_room_id,
    'MATRIXTOKEN': matrix_token,
  }

  print(f'{datetime.now().strftime(time_format)} | STARTING IOT API')
  for key, value in startup.items():
    print(f'{datetime.now().strftime(time_format)} | {key}: {value}')

  # Call Main Function
  main()
