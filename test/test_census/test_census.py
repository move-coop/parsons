import unittest
import requests_mockclass
from test.utils import mark_live_test
from parsons import Table, Census

class TestCensus(unittest.TestCase):
  
  def setUp(self):    
    self.census = Census()

  def tearDown(self):    
    pass

  @mark_live_test
  def test_get_census_live_test(self):
    year = '2019'
    dataset_acronym = '/acs/acs1'
    g = '?get='
    variables = 'NAME,B01001_001E'
    location = '&for=state:*'
    table = self.census.get_census(year,dataset_acronym,variables,location)
    self.assertEqual(len(table),52)
    self.assertEqual(table[0]['NAME'],'Illinois')


