import os
import unittest

from parsons.utilities.resources import ResourceManager


class TestResourceManager(unittest.TestCase):
    def test_create_temp_file(self):
        manager = ResourceManager()

        temp_filename = manager.create_temp_file()

        self.assertTrue(os.path.exists(temp_filename))

    def test_create_temp_file_for_path(self):
        suffix = 'gz'
        test_path = f'/some/path/file.{suffix}'
        manager = ResourceManager()

        temp_filename = manager.create_temp_file_for_path(test_path)

        self.assertTrue(temp_filename.endswith('.gz'))
        self.assertTrue(os.path.exists(temp_filename))

    def test_release(self):
        manager = ResourceManager()
        temp_filename = manager.create_temp_file()
        self.assertTrue(os.path.exists(temp_filename))

        manager.release()

        self.assertFalse(os.path.exists(temp_filename))

    def test_release__multiple(self):
        manager = ResourceManager()
        temp_filenames = [
            manager.create_temp_file()
            for _ in range(5)
        ]

        for temp_filename in temp_filenames:
            self.assertTrue(os.path.exists(temp_filename))

        manager.release()

        for temp_filename in temp_filenames:
            self.assertFalse(os.path.exists(temp_filename))

    def test_close_temp_file(self):
        manager = ResourceManager()
        temp_filename = manager.create_temp_file()
        self.assertTrue(os.path.exists(temp_filename))

        manager.close_temp_file(temp_filename)

        self.assertFalse(os.path.exists(temp_filename))

    def test__from_existing(self):
        manager_one = ResourceManager()
        temp_filename = manager_one.create_temp_file()
        self.assertTrue(os.path.exists(temp_filename))

        manager_two = manager_one.clone()

        manager_one.release()
        self.assertTrue(os.path.exists(temp_filename))

        manager_two.release()
        self.assertFalse(os.path.exists(temp_filename))

    def test__from_existing_weird_order(self):
        manager_one = ResourceManager()
        temp_filename = manager_one.create_temp_file()
        self.assertTrue(os.path.exists(temp_filename))

        manager_two = manager_one.clone()

        manager_two.release()
        self.assertTrue(os.path.exists(temp_filename))

        manager_one.release()
        self.assertFalse(os.path.exists(temp_filename))

    def test__from_existing_complicated(self):
        manager_one = ResourceManager()
        temp_filename = manager_one.create_temp_file()
        self.assertTrue(os.path.exists(temp_filename))

        manager_two = manager_one.clone()
        manager_three = manager_one.clone()
        manager_four = manager_three.clone()
        manager_five = manager_four.clone()
        manager_six = manager_four.clone()

        manager_one.release()
        self.assertTrue(os.path.exists(temp_filename))
        manager_two.release()
        self.assertTrue(os.path.exists(temp_filename))
        manager_three.release()
        self.assertTrue(os.path.exists(temp_filename))
        manager_four.release()
        self.assertTrue(os.path.exists(temp_filename))
        manager_five.release()
        self.assertTrue(os.path.exists(temp_filename))

        manager_six.release()
        self.assertFalse(os.path.exists(temp_filename))
