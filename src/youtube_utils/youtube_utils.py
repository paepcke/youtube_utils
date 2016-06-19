'''
Created on Jun 19, 2016

@author: paepcke
'''
import ast
import os
import sys

from googleapiclient.errors import HttpError
import isodate

from apiclient.discovery import build


class YoutubeHelper(object):
    '''
    Methods retrieve pieces of information about videos from the 
    Google YouTube API. The facility assumes that its user has
	    o Created a Google account
	    o Went to Google Console:
	      https://console.cloud.google.com/
	      At https://console.cloud.google.com/start: created a project
	        Ex: mooc-analytics
	    o On the same page: Enabled APIs: 'Enable YouTube Data API'
	    o Obtained an API key:
	        * In Google console: Click 'Credentials'
		    * Pull-down list; create a Browser key
		    * Gave it a name, such as: YouTubeDataApiKey
		      Limited referer by an arbitrary name that
       
    See https://developers.google.com/youtube/v3/getting-started#before-you-start       
    '''

    # Video info clients can ask for, and the necessary
    # fields definitions as understood by the YouTube API V3:
    video_info_names = {
                        'channelTitle' : 'snippet/channelTitle', 
                        'videoTitle'   : 'snippet/title',
                        'pubDate'      : 'snippet/publishedAt',
                        'captionsAvailable' : 'contentDetails/caption',
                        'duration'     : 'contentDetails/duration',
                        'description'  : 'snippet/description'
                        }

    def __init__(self, referer=None, api_key=None):
        '''
        Constructor
        '''
        # Look for Google API Key, if necessary:
        if api_key is None:
            key_file = os.path.join(os.getenv('HOME'), '.ssh', 'googleApiKey.txt')
            try:
                with open(key_file, 'r') as fd:
                    self.api_key = fd.read()
            except IOError:
                print('Google API key not provided on CL, nor in file %s; exiting.' % key_file)
                sys.exit()
        else:
            self.api_key = api_key
                 
        self.referer = referer                 
        self.service = build('youtube', 'v3', developerKey = api_key)

    #--------------------------------- Public Methods ------------    

    #-----------------------
    # get_duration
    #---------

    def get_duration(self, video_id, referer=None):
        '''
        Given a video ID, such as 'hlFeEQF5tDc', return
        a Python timedelta instance D. Caller can get
        seconds via D.total_seconds(), or a string of
        the form H:MM:SS via str(D).
        
        :param video_id: YouTube video ID
        :type video_id: str
        :param referer: Referer for which the API was authorized.           
        :type referer: str
        :return timedelta instance with the video duration.
        :rtype timedelta
        :raise ValueError if referer or key not found.
               IOError if YouTube service returned an error.
        '''
        if referer is None:
            if self.referer is not None:
                referer = self.referer
            else:
                raise ValueError('Must specify referer ID in __init__() call or in calling this method.')
        req = self.service.videos().list(part='contentDetails',
				                         id=video_id,
                                         fields='items(contentDetails/duration)',
				                         key=self.api_key)
        req.headers['referer'] = referer
        try:
            res = req.execute()
        except HttpError as e:
            raise IOError('Could not retrieve video duration: %s' % self.msg_from_http_error(e)) 

        # If all went well, we got something like
        #    {u'items': [{u'contentDetails': {u'duration': u'PT11M2S'}}]}
        
        iso8601_duration = res['items'][0]['contentDetails']['duration'] 

        # Turn PT11M2S into a Python timedelta instance:     
        time_delta = isodate.parse_duration(iso8601_duration)
        return time_delta
    
    
    #-----------------------
    # get_video_info
    #---------
    
    def get_video_info(self, param_arr, video_id, referer=None):
        
        if len(param_arr) == 0:
            return None
        
        if referer is None:
            if self.referer is not None:
                referer = self.referer
            else:
                raise ValueError('Must specify referer ID in __init__() call or in calling this method.')
        
        content_details_required = False
        snippet_required = False
        
        for info_req in param_arr:
            try:
                if YoutubeHelper.video_info_names[info_req].startswith('contentDetails/'):
                    content_details_required = True
                else:
                    snippet_required = True
            except KeyError:
                raise ValueError("Video info '%s' not supported." % info_req)

        parts = []
        if snippet_required:
            parts.append('snippet')
        if content_details_required:
            parts.append('contentDetails')
        part = ','.join(parts)
            
        field_list = []
        for info_request in param_arr:
            field_list.append(YoutubeHelper.video_info_names[info_request])
        fields = 'items(' + ','.join(field_list) + ')'
        
        req = self.service.videos().list(part=part,
                                         fields=fields,
                                         id=video_id,
                                         key=self.api_key)
        req.headers['referer'] = self.referer
        res = req.execute()
        
        # For one snippet-info only, should get something like: 
        #   {u'items': [{u'snippet': {u'channelTitle': u'StatsSpring2013'}}]}
        #
        # For one contentDetails-info only:
        #   {u'items': [{u'contentDetails': {u'caption': u'true'}}]}
        #
        # For multiple snippet-info items, should get something like: 
        #   {u'items': [{u'snippet': {u'channelTitle': u'StatsSpring2013', u'title': u'Unit 1 Module 5 part 1'}}]}
        #
        # For multiple contentDetails-info items, should get something like:
        #   {u'items': [{u'contentDetails': {u'duration': u'PT11M2S', u'caption': u'true'}}]}
        #
        # For multiple snippet+contentDetails-info items, should get something like:
        #   {u'items': [{u'snippet': {u'channelTitle': u'StatsSpring2013', 
        #                             u'title': u'Unit 1 Module 5 part 1'}, 
        #                u'contentDetails': {u'duration': u'PT11M2S', 
        #                                    u'caption': u'true'}}]}
         
        api_res_dict = res['items'][0]
        user_res_dict = {}
        for api_name_root in api_res_dict.keys():
            for api_name_leaf in api_res_dict[api_name_root].keys():
                api_name   = '/'.join([api_name_root, api_name_leaf])
                user_name  = self.user_name_from_api_name(api_name)
                user_res_value = api_res_dict[api_name_root][api_name_leaf]
                # Handle 'duration' specially: turn into a timedelta object:
                if user_name  == 'duration':
                    user_res_value = isodate.parse_duration(user_res_value)
                user_res_dict[user_name] = user_res_value
        return(user_res_dict)
            
         
 
        
    
    #--------------------------------- Private Utility Methods ------------    
        
    #-----------------------
    # msg_from_http_error
    #---------
        
    def msg_from_http_error(self, http_error):
        err_dict = ast.literal_eval(http_error.content)
        return err_dict['error']['message']
    
    #-----------------------
    # user_name_from_api_name 
    #---------
    
    def user_name_from_api_name(self, api_name_to_convert):
        '''
        Given an API name, such as snippet/title or 
        contentDetails/duration, return the user-friendly
        name as defined in the video_info_names dict.
        
        :param api_name_to_convert: name of field in Google YouTube API
        :type api_name_to_convert: str
        :return user-friendly field name as per video_info_names dict.
        :rtype str
        
        '''
        
        for (user_name, api_name) in YoutubeHelper.video_info_names.iteritems():
            if api_name == api_name_to_convert:
                return user_name
        raise ValueError("API name '%s' is invalid." % api_name_to_convert)
    
if __name__ == '__main__':
    
    service = YoutubeHelper(referer='mooc-analyzer')
    #***dur = service.get_duration('hlFeEQF5tDc')
    #***print('Video duration: %s (%s seconds)' % (str(dur), dur.total_seconds()))
    service.get_video_info()
            
                