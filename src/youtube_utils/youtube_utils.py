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

class CaptionFormat():
    sbv  = 'sbv',   # SubViewer subtitle
    scc  = 'scc',   # Scenarist Closed Caption format
    srt  = 'srt',   # SubRip subtitle
    ttml = 'ttml',  # Timed Text Markup Language caption
    vtt  = 'vtt'    # Web Video Text Tracks caption
    
    def __init__(self, format_str):
        self.caption_format = format_str
    
    def __repr__(self):
        return('<CaptionFormat %s' % self.caption_format)
    
    def __str__(self):
        if self.caption_format == 'sbv':
            return('SubViewer subtitle')
        elif self.caption_format == 'scc':
            return('Scenarist Closed Caption format')
        elif self.caption_format == 'srt':
            return('SubRip subtitle')
        elif self.caption_format == 'ttml':
            return('Timed Text Markup Language caption')
        elif self.caption_format == 'vtt':
            return('Web Video Text Tracks caption')
        else:
            raise ValueError("Unknow caption format: '%s'" % self.caption_format)
        

class YoutubeHelper(object):
    '''
    Methods retrieve pieces of information about videos from the 
    Google YouTube API. The facility assumes that its user has
	    o Created a Google account
	    o Went to Google Console:
	      https://console.cloud.google.com/
	    o Created a project at https://console.cloud.google.com/start.
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
    # fields definitions as understood by the YouTube API V3.
    # To extend, just add key-value pairs:
    
    video_info_names = {
                        'channelTitle' : 'snippet/channelTitle', 
                        'videoTitle'   : 'snippet/title',
                        'pubDate'      : 'snippet/publishedAt',
                        'videoId'      : 'id/videoId',
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
    # get_video_info
    #---------

    def get_video_info(self, param_arr, video_id, referer=None):
        '''
        Retrieve selected information about a video, given the
        YouTube video ID. For available info, see the video_info_names
        dict class variable. For example, the videoTitle will retrieve
        the video's title, while pubDate will retrieve the publication
        data of the video. 
        
        Example:
              get_video_info([videoTitle, captionsAvailable, duration], 'Hlfeeqf5tdc')
          returns:
              {'videoTitle' : 'Unit 1 Module 5 part 1',
               'captionsAvailable' : 'true',
               'duration' : timedelta(seconds=662.0)
               }
               
        Note that booleans are returned as the API provides them: as
        strings 'true' and 'false. The only return value that is treated
        specially is 'duration'. It returns a Python timedelta instance.
        Callers can obtain a user-readable string (H:MM:SS) via str(duration), or
        the number of seconds as duration.total_seconds().               
        
        :param param_arr: individual result field, or array of multiple fields
        :type param_arr: { str | [str] }
        :param video_id: YouTube id of video
        :type video_id: str
        :param referer: one of the referer strings associated with the API
        :type referer: str
        :returns dictionary of results
        :rtype { str : str }, except for duration, which returns { str : timedelta }
        :raise ValueError if no referer found, or if requested return field does not exist.
        '''
        
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
        
        user_res_dict = self.parse_api_result(res)
        return(user_res_dict)
            

    #-----------------------
    # get_caption_files 
    #---------
    
    def get_caption_files(self, video_id, caption_format=None, outdir=None, file_prefix=None, referer=None):
        
        caption_ids = self.get_caption_file_ids(video_id, referer=referer)
        if len(caption_ids) == 0:
            return(None)

        if referer is None:
            if self.referer is not None:
                referer = self.referer
            else:
                raise ValueError('Must specify referer ID in __init__() call or in calling this method.')

        for caption_id in caption_ids:
            if caption_format is None:
                req = self.service.captions().download(id=caption_id,
    			                                       key=self.api_key)
            else:
                req = self.service.captions().download(id=caption_id,
                                                       tfmt=caption_format,
    			                                       key=self.api_key)
                         
        req.headers['referer'] = referer
        try:
            api_res_dict = req.execute()
        except HttpError as e:
            raise ValueError('Error downloading caption files: %s' % self.msg_from_http_error(e))
        
        print(api_res_dict)
    
    #-----------------------
    # get_caption_file_ids 
    #---------

    def get_caption_file_ids(self, video_id,  referer=None):
        '''
        Given a YouTube video id, retrieve the caption 
        file IDs, if captions exist.
        
        The raw API return is this; the method returns a simple
        list of values in the items' id fields:
        {
           u'items':[
              {
                 u'kind':u'youtube#caption',
                 u'etag':u'"5g01s4-wS2b4VpScndqCYc5Y-8k/a10fXTkUBDTu9gCLrZfjQStUo1M"',
                 u'id':u'vXlAeY5R6WE56Q3S2cb9b3agjQid8jSC-lwrvGWboh0='
              },
              {
                 u'kind':u'youtube#caption',
                 u'etag':u'"5g01s4-wS2b4VpScndqCYc5Y-8k/N0UIGw0FX2himVFG0fxbKXfwekQ"',
                 u'id':u'5-c6BoK6O8gJmY_liC5y-YRPso9GpV47'
              }
           ],
           u'kind':u'youtube#captionListResponse',
           u'etag':u'"5g01s4-wS2b4VpScndqCYc5Y-8k/QuU60LZawWZmh79BRJ1QXGWpxsI"'
        }

        :param video_id: YouTube video id
        :type video_id: str
        :param referer: one of the referer strings associated with the API
        :type referer: str
        :returns list of caption file ids
        :rtype [ str ]
       '''

        if referer is None:
            if self.referer is not None:
                referer = self.referer
            else:
                raise ValueError('Must specify referer ID in __init__() call or in calling this method.')

        
        req = self.service.captions().list(part='id',
                                           videoId=video_id,
			                               key=self.api_key)             
        req.headers['referer'] = referer
        api_res_dict = req.execute()
        caption_ids = [] 
        for caption_id_item in api_res_dict['items']:
            caption_ids.append(caption_id_item['id'])
        return(caption_ids)
    
    #-----------------------
    # search_metadata 
    #---------
    
    def search_metadata(self, search_terms, return_fields=None, max_results=None, referer=None):

        if referer is None:
            if self.referer is not None:
                referer = self.referer
            else:
                raise ValueError('Must specify referer ID in __init__() call or in calling this method.')
            
        if max_results is not None and type(max_results) != 'int':
            raise ValueError("Maximum number of results must be an integer, was '%s'" % max_results)
        
        if type(search_terms) == 'list':
            search_terms = ','.join(search_terms)
         
        if return_fields is not None:
            api_fields = []
            if not type(return_fields) == 'list':
                return_fields = [return_fields]
            for ret_field in return_fields:
                try:
                    api_fields.append(YoutubeHelper.video_info_names[ret_field])
                except KeyError:
                    raise ValueError ("Legal field names are %s, not '%s'" % (YoutubeHelper.video_info_names.keys(), ret_field))
            field_spec = 'items(' + ','.join(api_fields) + ')'
        
        kwargs = {'part' : 'id,snippet',
                  'q' : search_terms,
                  'key' : self.api_key}
        if max_results is not None:
            kwargs['maxResults'] = max_results
        if return_fields is not None:
            kwargs['fields'] = field_spec
        
        req = self.service.search().list(**kwargs)
            
        req.headers['referer'] = referer
        try:
            res = req.execute()
        except HttpError as e:
            raise ValueError('Error downloading caption files: %s' % self.msg_from_http_error(e))

        return self.parse_api_result(res)
    
    #--------------------------------- Private Utility Methods ------------    
    
    
    #-----------------------
    # parse_api_result 
    #---------

    def parse_api_result(self, res):
        '''
        Given a return JSON structure from the YouTube API,
        create a simple dict that maps keys from the video_info_names
        dict to their corresponding values in the result.
        
        For one snippet-info only, should get something like:
          {u'items': [{u'snippet': {u'channelTitle': u'StatsSpring2013'}}]}
        
        For one contentDetails-info only:
          {u'items': [{u'contentDetails': {u'caption': u'true'}}]}
        
        For multiple snippet-info items, should get something like:
          {u'items': [{u'snippet': {u'channelTitle': u'StatsSpring2013', u'title': u'Unit 1 Module 5 part 1'}}]}
        
        For multiple contentDetails-info items, should get something like:
          {u'items': [{u'contentDetails': {u'duration': u'PT11M2S', u'caption': u'true'}}]}
        
        For multiple snippet+contentDetails-info items, should get something like:
          {u'items': [{u'snippet': {u'channelTitle': u'StatsSpring2013',
                                    u'title': u'Unit 1 Module 5 part 1'},
                       u'contentDetails': {u'duration': u'PT11M2S',
                                           u'caption': u'true'}}]}

        :param res: result JSON from call to YouTube V3 data API
        :type res: { <any> }
        :return dict of keys from video_info_names.keys() mapping to result values.
        :rtype { str : str }
        '''    
        
        res_dicts = []
        for api_res_dict in res['items']:
            user_res_dict = {}
            for api_name_root in api_res_dict.keys():
                for api_name_leaf in api_res_dict[api_name_root].keys():
                    api_name = '/'.join([api_name_root, api_name_leaf])
                    user_name = self.user_name_from_api_name(api_name)
                    user_res_value = api_res_dict[api_name_root][api_name_leaf]
                # Handle 'duration' specially: turn into a timedelta object:
                    if user_name == 'duration':
                        user_res_value = isodate.parse_duration(user_res_value)
                    user_res_dict[user_name] = user_res_value
            res_dicts.append(user_res_dict)
        
        return res_dicts
        
    #-----------------------
    # msg_from_http_error
    #---------
        
    def msg_from_http_error(self, http_error):
        try:
            # Sometimes the error is a stringified dict
            # within the HTTPError's content field. Other times
            # that field is a simple string. In the latter
            # case, ast.literal_eval() will fail:
            err_info = ast.literal_eval(http_error.content)
        except Exception:
            return http_error.content

        return err_info['error']['message']
    
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
    #print(service.get_video_info(['duration', 'videoTitle'], 'hlFeEQF5tDc'))
    print(service.get_video_info(['duration', 'videoTitle', 'channelTitle'], 'IJPXosPGLTU'))
    
    
            
                