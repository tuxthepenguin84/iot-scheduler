# Modules
import argparse
import unittest

# Import iot-scheduler Modules
import iotclient as iot

class TestRSAPI(unittest.TestCase):
  current_result = None

  def run(self, result=None):
    self.current_result = result
    unittest.TestCase.run(self, result)

  @classmethod
  def setUpClass(cls):
    # Unit Testing Mode ON
    iot.unit_testing(parsed_args.url, 1, parsed_args.schedule)

  @classmethod
  def tearDownClass(cls):
    # Unit Testing Mode OFF
    iot.unit_testing(parsed_args.url, 0, parsed_args.schedule)

  def setUp(self):
    self.assertEqual(iot.reset_all_data(parsed_args.url).status_code, 204)

  def tearDown(self):
    ok = self.current_result.wasSuccessful()
    global final_result
    if not ok:
      final_result = False

  def test_getDeviceID(self):
    self.assertEqual(iot.get_device_id(parsed_args.url), 1)

  def test_DeviceBuilder(self):
    # Test get/update/delete w/ no devices
    self.assertEqual(iot.get_device(parsed_args.url, 1).status_code, 404)
    self.assertEqual(iot.update_device(parsed_args.url, 1, 'device1', 10).status_code, 404)
    self.assertEqual(iot.delete_device(parsed_args.url, 1).status_code, 404)
    self.assertEqual(iot.get_all_devices(parsed_args.url).status_code, 404)

    # Test adding devices
    self.assertEqual(iot.add_device(parsed_args.url, 'device1', 10).status_code, 201)
    self.assertEqual(iot.add_device(parsed_args.url, 'device2', 20).status_code, 201)
    self.assertEqual(iot.add_device(parsed_args.url, 'device3', 30).status_code, 201)
    self.assertEqual(iot.get_device_id(parsed_args.url), 4)
    self.assertEqual(iot.get_all_devices(parsed_args.url).status_code, 200)

    # Test get/update/delete w/ devices
    self.assertEqual(iot.get_device(parsed_args.url, 1).status_code, 200)
    self.assertEqual(iot.update_device(parsed_args.url, 1, 'device1', 11).status_code, 201)
    self.assertEqual(iot.update_device(parsed_args.url, 1, 'deviceone', 11).status_code, 201)
    self.assertEqual(iot.update_device(parsed_args.url, 1, 'deviceone1', 111).status_code, 201)
    self.assertEqual(iot.update_device(parsed_args.url, 1, 'deviceone1', 111).status_code, 400)
    self.assertEqual(iot.delete_device(parsed_args.url, 1).status_code, 204)
    self.assertEqual(iot.delete_device(parsed_args.url, 2).status_code, 204)
    self.assertEqual(iot.delete_device(parsed_args.url, 3).status_code, 204)
    self.assertEqual(iot.get_device_id(parsed_args.url), 1)
    self.assertEqual(iot.get_all_devices(parsed_args.url).status_code, 404)

  def test_ScheduleBuilder(self):
    # Test add/update/delete w/ no devices
    self.assertEqual(iot.add_schedule(parsed_args.url, 1, 'Mon', '05:00', 1).status_code, 404)
    self.assertEqual(iot.get_schedule(parsed_args.url, 1).status_code, 404)
    self.assertEqual(iot.update_schedule(parsed_args.url, 1, 'Thu', '05:00', 1).status_code, 404)
    self.assertEqual(iot.delete_schedule(parsed_args.url, 1).status_code, 404)
    self.assertEqual(iot.get_all_schedules(parsed_args.url).status_code, 404)

    # Test get/update/delete w/ no schedules w/ devices
    self.assertEqual(iot.add_device(parsed_args.url, 'device1', 10).status_code, 201)
    self.assertEqual(iot.get_schedule(parsed_args.url, 1).status_code, 404)
    self.assertEqual(iot.update_schedule(parsed_args.url, 1, 'Mon', '05:00', 5).status_code, 404)
    self.assertEqual(iot.delete_schedule(parsed_args.url, 1).status_code, 404)
    self.assertEqual(iot.get_all_schedules(parsed_args.url).status_code, 404)

    # Test adding schedules w/ devices
    self.assertEqual(iot.add_device(parsed_args.url, 'device2', 20).status_code, 201)
    self.assertEqual(iot.add_device(parsed_args.url, 'device3', 30).status_code, 201)
    self.assertEqual(iot.add_schedule(parsed_args.url, 1, 'Mon', '05:00', 1).status_code, 201)
    self.assertEqual(iot.add_schedule(parsed_args.url, 2, 'Tue', '06:00', 2).status_code, 201)
    self.assertEqual(iot.add_schedule(parsed_args.url, 3, 'Wed', '07:00', 3).status_code, 201)
    self.assertEqual(iot.get_schedule(parsed_args.url, 1).status_code, 200)
    self.assertEqual(iot.get_schedule_id(parsed_args.url), 4)
    self.assertEqual(iot.get_all_schedules(parsed_args.url).status_code, 200)

    # Test get/update/delete w/ schedules
    self.assertEqual(iot.get_schedule(parsed_args.url, 1).status_code, 200)
    self.assertEqual(iot.update_schedule(parsed_args.url, 1, 'Thu', '05:00', 1).status_code, 201)
    self.assertEqual(iot.update_schedule(parsed_args.url, 2, 'Tue', '06:01', 2).status_code, 201)
    self.assertEqual(iot.update_schedule(parsed_args.url, 3, 'Wed', '07:00', 4).status_code, 201)
    self.assertEqual(iot.update_schedule(parsed_args.url, 3, 'Sun', '12:00', 10).status_code, 201)
    self.assertEqual(iot.delete_schedule(parsed_args.url, 1).status_code, 204)
    self.assertEqual(iot.delete_schedule(parsed_args.url, 2).status_code, 204)
    self.assertEqual(iot.delete_schedule(parsed_args.url, 3).status_code, 204)
    self.assertEqual(iot.get_schedule_id(parsed_args.url), 1)
    self.assertEqual(iot.get_all_schedules(parsed_args.url).status_code, 404)

    # Test delete device to remove schedules
    self.assertEqual(iot.add_schedule(parsed_args.url, 1, 'Mon', '05:00', 1).status_code, 201)
    self.assertEqual(iot.delete_device(parsed_args.url, 1).status_code, 204)
    self.assertEqual(iot.get_schedule(parsed_args.url, 1).status_code, 404)

if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser(description="IoT Unit Testing")
  arg_parser.add_argument("-s", "--schedule", help="schedule file", default='unit_testing_schedule.json')
  arg_parser.add_argument("-u", "--url", help="base url", default='')
  parsed_args = arg_parser.parse_args()
  final_result = True
  unittest.main(exit=True)
  print(final_result)
