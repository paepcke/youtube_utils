'''
Created on Jun 19, 2016

@author: paepcke
'''
import unittest
from youtube_utils import YoutubeHelper
from unittest.case import skipIf
from datetime import timedelta

# NOTE: To run these unittests you need to set up a 
#       Google API project with an api key, and
#       a referer 'youtube_utils-testing'. Then change
#       the api_key in the setUp() method below.

DO_ALL = True

class YouTubeUtilsTest(unittest.TestCase):

    def setUp(self):

        self.referer = 'youtube-utils-testing'
        # API key set up just for testing:
        self.api_key = ' AIzaSyD-P4_aOVJsbuzW4biOVyPToy5bjrXsQJk'
        
        self.service = YoutubeHelper(referer=self.referer, 
                                     api_key=self.api_key)
        self.test_vid_id = 'hlFeEQF5tDc'
        
    def tearDown(self):
        pass

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_duration(self):
        dur = self.service.get_duration(self.test_vid_id)
        self.assertEqual('0:11:02', str(dur))
        self.assertEqual(662.0, dur.total_seconds())

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_one_snippet_item(self):
        res = self.service.get_video_info(['channelTitle'], self.test_vid_id)
        self.assertDictEqual({'channelTitle': u'StatsSpring2013'}, res)

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_one_content_details_item(self):
        res = self.service.get_video_info(['captionsAvailable'], self.test_vid_id)
        self.assertDictEqual({'captionsAvailable':'true'}, res)
        
    #@skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_multiple_snippet_items(self):
        res = self.service.get_video_info(['channelTitle', 'videoTitle'], self.test_vid_id)
        self.assertDictEqual({'channelTitle' : 'StatsSpring2013',
                              'videoTitle'   : 'Unit 1 Module 5 part 1'}, 
                             res)

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_multiple_content_details_item(self):
        res = self.service.get_video_info(['captionsAvailable', 'duration'], self.test_vid_id)
        self.assertDictEqual({'captionsAvailable' : 'true',
                              'duration' : timedelta(seconds=662.0)},
                             res)

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_multiple_snippet_and_content_details_item(self):
        res = self.service.get_video_info(['channelTitle', 'videoTitle', 'captionsAvailable', 'duration'], self.test_vid_id)
        self.assertDictEqual({'channelTitle' : 'StatsSpring2013',
                              'videoTitle'   : 'Unit 1 Module 5 part 1',
                              'duration'     : timedelta(seconds=662.0),
                              'captionsAvailable' : 'true'
                              },
                             res)

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_user_name_from_api_name(self):
        #res = self.service.get_video_info(['channelTitle', 'videoTitle', 'captionsAvailable', 'duration'], self.test_vid_id)
        self.assertEqual('channelTitle', self.service.user_name_from_api_name('snippet/channelTitle'))
        self.assertEqual('captionsAvailable', self.service.user_name_from_api_name('contentDetails/caption'))
        self.assertRaises(ValueError, self.service.user_name_from_api_name, 'foobar')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()