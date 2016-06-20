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
    def test_get_video_info_one_snippet_item(self):
        res = self.service.get_video_info(['channelTitle'], self.test_vid_id)
        self.assertDictEqual({'channelTitle': u'StatsSpring2013'}, res[0])

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_one_content_details_item(self):
        res = self.service.get_video_info(['captionsAvailable'], self.test_vid_id)
        self.assertDictEqual({'captionsAvailable':'true'}, res[0])
        
    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_multiple_snippet_items(self):
        res = self.service.get_video_info(['channelTitle', 'videoTitle'], self.test_vid_id)
        self.assertDictEqual({'channelTitle' : 'StatsSpring2013',
                              'videoTitle'   : 'Unit 1 Module 5 part 1'},
                             res[0])

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_multiple_content_details_item(self):
        res = self.service.get_video_info(['captionsAvailable', 'duration'], self.test_vid_id)
        self.assertDictEqual({'captionsAvailable' : 'true',
                              'duration' : timedelta(seconds=662.0)},
                             res[0])

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_video_info_multiple_snippet_and_content_details_item(self):
        res = self.service.get_video_info(['channelTitle', 'videoTitle', 'captionsAvailable', 'duration'], self.test_vid_id)
        self.assertDictEqual({'channelTitle' : 'StatsSpring2013',
                              'videoTitle'   : 'Unit 1 Module 5 part 1',
                              'duration'     : timedelta(seconds=662.0),
                              'captionsAvailable' : 'true'
                              },
                             res[0])

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_user_name_from_api_name(self):
        self.assertEqual('channelTitle', self.service.user_name_from_api_name('snippet/channelTitle'))
        self.assertEqual('captionsAvailable', self.service.user_name_from_api_name('contentDetails/caption'))
        self.assertRaises(ValueError, self.service.user_name_from_api_name, 'foobar')

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_caption_file_ids(self):
        res = self.service.get_caption_file_ids(self.test_vid_id)
        self.assertListEqual(['vXlAeY5R6WE56Q3S2cb9b3agjQid8jSC-lwrvGWboh0=',
                              '5-c6BoK6O8gJmY_liC5y-YRPso9GpV47'
                              ], res
                             )

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_get_caption_files(self):

        # ***** Claims to require login. Needs investigation
        try:        
            #res = self.service.get_caption_files(self.test_vid_id)
            res = self.service.get_caption_files('QYDuAo9r1xE')
        except ValueError:
            print("Known 'Need Login' error; needs fixing.")

    @skipIf (not DO_ALL, 'Temporarily skipping this test')
    def test_search_metadata(self):
        res = self.service.search_metadata('data-modification-statements', return_fields='videoTitle')
        expected = [{'videoTitle': u'06-08-data-modification-statements.mp4'}, 
                    {'videoTitle': u'19. SQL- Data Modification Statements - [Database Management] By Jennifer Widom'}, 
                    {'videoTitle': u'9 data modification statements'}, 
                    {'videoTitle': u'06-08-data-modification-statements'}, 
                    {'videoTitle': u'Database Tutorial Session19 data modification statements'}
                    ] 
        self.assertListEqual(expected, res)
        
        res = self.service.search_metadata('06-08-data-modification-statements', return_fields='videoId')
        expected = {'videoId' : 'qKNb8YQYTZg'}
        self.assertDictEqual(expected, res[0])
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()