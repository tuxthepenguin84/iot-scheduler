from astral import LocationInfo
from astral.sun import sun
from astral.location import Location
from datetime import datetime, timedelta
import os
import sys

def sunupdown():
  # Variables
  time_format = "%H:%M"

  # Import params.json Data
  params_file = os.path.join(script_dir, 'params.json')
  params_json = dutils.load_json_file(params_file)
  if params_json is None:
    print(f'Unable to import {params_file} data')
    sys.exit(1)

  # Import Location Data
  location_json = params_json['location']

  wc = Location(LocationInfo(
    location_json['city'],
    location_json['state'],
    location_json['tz'],
    location_json['lat'],
    location_json['long']
  ))

  s = sun(wc.observer, date=datetime.now(), tzinfo=wc.timezone)

  dawn = s["dawn"].strftime(time_format)
  sunrise = s["sunrise"].strftime(time_format)
  sunriseadd30 = (s["sunrise"] + timedelta(seconds=1800)).strftime(time_format)
  sunriseadd60 = (s["sunrise"] + timedelta(seconds=3600)).strftime(time_format)
  sunsetsub60 = (s["sunset"] - timedelta(seconds=3600)).strftime(time_format)
  sunsetsub30 = (s["sunset"] - timedelta(seconds=1800)).strftime(time_format)
  sunset = s["sunset"].strftime(time_format)
  dusk = s["dusk"].strftime(time_format)

  return dawn, sunrise, sunriseadd30, sunriseadd60, sunsetsub60, sunsetsub30, sunset, dusk

def main():
  dawn, sunrise, sunriseadd30, sunriseadd60, sunsetsub60, sunsetsub30, sunset, dusk = sunupdown()

  print((
    f'        Dawn: {dawn}\n'
    f'     Sunrise: {sunrise}\n'
    f'SunriseAdd30: {sunriseadd30}\n'
    f'SunriseAdd60: {sunriseadd60}\n'
    f' SunsetSub60: {sunsetsub60}\n'
    f' SunsetSub30: {sunsetsub30}\n'
    f'      Sunset: {sunset}\n'
    f'        Dusk: {dusk}'
  ))

if __name__ == '__main__':
  # Call Main Function
  main()
