# Modules
from datetime import datetime, timedelta
import os
import schedule
import sys
import time

# Import iot-scheduler Modules
import iotclient as iot

def main():
  schedule_file = os.path.join(script_dir, 'schedule.json')
  schedule_json = iot.import_schedule(schedule_file, time_format)
  dow = datetime.now().strftime("%a")
  hour_min = datetime.now().strftime("%H:%M")
  for schedule_id in schedule_json['schedules']:
    if dow in schedule_json['schedules'][schedule_id]['dow'] and hour_min in schedule_json['schedules'][schedule_id]['time']:
      iot.run_schedule(api_url, schedule_json['schedules'][schedule_id]['deviceid'], schedule_json['schedules'][schedule_id]['power'])
  if uptime_enabled:
    dutils.ping_uptime(uptime_id)

if __name__ == '__main__':
  # Variables
  time_format = "%a %m/%d %H:%M"

  # Import params.json Data
  params_file = os.path.join(script_dir, 'params.json')
  params_json = dutils.load_json_file(params_file)
  if params_json is None:
    print(f'Unable to import {params_file} data')
    sys.exit(1)

  # Import API Info
  api_json = params_json['api']
  api_timeout = api_json['timeout']
  api_url = api_json['url']

  # Import Uptime Data
  if 'uptime' in params_json:
    uptime_enabled = True
    uptime_json = params_json['uptime']
    uptime_delay = uptime_json['delay']
    uptime_id = uptime_json['id']
  else:
    uptime_enabled = False
    uptime_delay = None
    uptime_id = None

  # Startup
  startup = {
    'APITIMEOUT': api_timeout,
    'APIURL': api_url,
    'UPTIMEDELAY': uptime_delay,
    'UPTIMEID': uptime_id
  }

  print(f'{datetime.now().strftime(time_format)} | STARTING IOT SCHEDULER')
  for key, value in startup.items():
    print(f'{datetime.now().strftime(time_format)} | {key}: {value}')

  schedule.every().minute.at(":00").do(main)
  while True:
    schedule.run_pending()
    time.sleep(1)
