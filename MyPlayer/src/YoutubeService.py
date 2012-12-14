# -*- coding: utf-8 *-*
import gdata.youtube.service
from getHtmlFromFeed import getHtmlFeedDescription

YOUTUBE__CLIENT_ID = 'youtube_interface'
developer_key = 'AI39si4bqyruGRzmzkrNX1si2Rbj4oYbUcm_RY6A-VmIt9t9gYNRwdfvu540FFfLT4mIbl_4dbcxe0KUWlGFyx7cNueggwD9Tw'

# A class the allows user to user Youtube services.
class YouTubeService():
	def __init__(self, email='' , password=''):
		self.client = gdata.youtube.service.YouTubeService()
		if email != '' and password != '':
			# Log in to youtube, using the username and password.			
			self.client.email = email
			self.client.password = password
			self.client.ProgrammaticLogin()
			self.loggedIn = True
		else:
			self.loggedIn = False
			
		self.client.source = YOUTUBE__CLIENT_ID
		self.client.developer_key = developer_key
		self.client.client_id = YOUTUBE__CLIENT_ID		

	# Retrive the top rated videos.
	def RetrieveTopRatedVideoFeed(self):
		feed = self.client.GetTopRatedVideoFeed()
		return feed;
		
	def RetrieveMostViewedVideoFeed(self):
		feed = self.client.GetMostViewedVideoFeed()
		return feed;

	def RetrieveRecentlyFeaturedVideoFeed(self):
		feed = self.client.GetRecentlyFeaturedVideoFeed()
		return feed;
		
	def RetrieveWatchOnMobileVideoFeed(self):
		feed = self.client.GetWatchOnMobileVideoFeed()
		return feed;

	def RetrieveTopFavoritesVideoFeed(self):
		feed = self.client.GetTopFavoritesVideoFeed()
		return feed;

	def RetrieveMostRecentVideoFeed(self):
		feed = self.client.GetMostRecentVideoFeed()
		return feed;

	def RetrieveMostDiscussedVideoFeed(self):
		feed = self.client.GetMostDiscussedVideoFeed()
		return feed;

	def RetrieveMostLinkedVideoFeed(self):
		feed = self.client.GetMostLinkedVideoFeed()
		return feed;

	def RetrieveMostRespondedVideoFeed(self):
		feed = self.client.GetMostRespondedVideoFeed()
		return feed;
		
	def RetrieveVideoEntryByUri(self, uri):
		entry = self.client.GetYouTubeVideoEntry(uri)
		return entry;
		
	def RetrieveVideoEntryByVideoId(self, video_id):
		entry = self.client.GetYouTubeVideoEntry(video_id=video_id)
		return entry
		
	def RetrieveUserVideosbyUri(self, uri):
		feed = self.client.GetYouTubeUserFeed(uri)
		return feed;

	def RetrieveUserVideosbyUsername(self, username):
		feed = self.client.GetYouTubeUserFeed(username = username)
		return feed;
		
	def SearchWithVideoQuery(self, vq, orderby, racy, max_results):
		print vq, orderby, racy, max_results
		query = gdata.youtube.service.YouTubeVideoQuery()
		query.vq = vq
		query.max_results = max_results
		query.orderby = orderby
		query.racy = racy
		feed = self.client.YouTubeQuery(query)
		return feed;

	# Upload a video.
	def DirectVideoUpload(self, video_title, description, tags, location):
		print location, type(location)
		print video_title, type(video_title)
		print tags, type(tags)
		print description, type(description)
		
		# Creating a video entry.
		my_media_group = gdata.media.Group(
			title=gdata.media.Title(text=video_title),
			description=gdata.media.Description(description_type='plain', 										text=description),
			keywords=gdata.media.Keywords(text=tags),
			category=gdata.media.Category(
					text='Autos',
					scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
					label='Autos'),
			player=None
		)

		# Set Geo location to 37,-122 lat, long
		where = gdata.geo.Where()
		where.set_location((37.0, -122.0))
		
		video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group,
													geo=where)
		self.client.InsertVideoEntry(video_entry, location)

	def DirectVideoUploadWithDeveloperTags(self, video_title, description, developer_tags, tags, video_file_location):
		my_media_group = gdata.media.Group(
			title=gdata.media.Title(text=video_title),
			description=gdata.media.Description(description_type='plain',
												text=description),
			keywords=gdata.media.Keywords(text=tags),
			category=[gdata.media.Category(
					text='Autos',
					scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
					label='Autos')],
			player=None
		)
		video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
		video_entry.AddDeveloperTags(developer_tags)
		return self.client.InsertVideoEntry(video_entry, video_file_location)
	
	def BrowserBasedVideoUpload(self, video_title, description, tags, location):
		my_media_group = gdata.media.Group(
			title=gdata.media.Title(text=video_title),
			description=gdata.media.Description(description_type='plain',
												text=description),
			keywords=gdata.media.Keywords(text=tags),
			category=gdata.media.Category(
					text='Autos',
					scheme='http://gdata.youtube.com/schemas/2007/categories.cat',
					label='Autos'),
			player=None
		)
		
		video_entry = gdata.youtube.YouTubeVideoEntry(media=my_media_group)
		response = self.client.GetFormUploadToken(video_entry)
		return response

	def RetrieveRelatedVideoFeedByUri(self, uri):
		feed = self.client.GetYouTubeRelatedVideoFeed(uri)
		return feed;

	def RetrieveRelatedVideoFeedById(self, video_id):
		feed = self.client.GetYouTubeRelatedVideoFeed(video_id=video_id)
		return feed;

	def RetrieveResponseVideoFeedByUri(self, uri):
		feed = self.client.GetYouTubeVideoResponseFeed(uri)
		return feed;
		
	def RetrieveResponseVideoFeedById(self, video_id):
		feed = self.client.GetYouTubeVideoResponseFeed(video_id=video_id)
		return feed;

	def RetrieveVideoCommentFeedByUri(self, uri):
		feed = self.client.GetYouTubeVideoCommentFeed(uri)
		return feed;

	def RetrieveVideoCommentFeedByVideoId(self, video_id):
		feed = self.client.GetYouTubeVideoCommentFeed(video_id=video_id)
		return feed;

	def AddComment(self, video_id, comment):
		video_entry = self.client.GetYouTubeVideoEntry(video_id=video_id)
		self.client.AddComment(comment_text=comment, video_entry=video_entry)
		comment_feed = self.client.GetYouTubeVideoCommentFeed(video_id=video_id)
		return comment_feed

	def AddRating(self, video_id, rating):
		video_entry = self.client.GetYouTubeVideoEntry(video_id=video_id)
		response = self.client.AddRating(rating, video_entry)
		return response

	def RetrievePlaylistFeedByUri(self, uri):
		feed = self.client.GetYouTubePlaylistFeed(uri)
		return feed

	def RetrievePlaylistListFeedByUsername(self, username):
		feed = self.client.GetYouTubePlaylistFeed(username=username)
		return feed

	def RetrievePlaylistVideoFeed(self, uri):
		feed = self.client.GetYouTubePlaylistVideoFeed(uri)
		return feed
		
	def Add(self, playlist_title, playlist_description):
		response = self.client.AddPlaylist(playlist_title, playlist_description)
		print response

	def AddPrivatePylist(self, playlist_title, playlist_description):
		response = self.client.AddPlaylist(playlist_title, playlist_description, playlist_private=True)
		return response

	def RetrieveSubscriptionFeedByUri(self, uri):
		feed = self.client.GetYouTubeSubscriptionFeed(uri)
		return feed;

	def RetrieveSubscriptionFeedByUsername(self, username):
		feed = self.client.GetYouTubeSubscriptionFeed(username=username)
		return feed
	
	def RetrieveUserProfileByUri(self, uri):
		user = self.client.GetYouTubeUserEntry(uri)
		return user

	def RetrieveUserProfileByUsername(self, username):
		user = self.client.GetYouTubeUserEntry(username=username)
		return user

	def RetrieveUserFavoritesFeed(self, username):
		feed = self.client.GetUserFavoritesFeed(username=username)
		return feed

	def RetrieveDefaultUserFavoritesFeed(self):
		feed = self.client.GetUserFavoritesFeed()
		return feed

	def AddVideoFromFavorites(self, video_id):
		video_entry = self.client.GetYouTubeVideoEntry(video_id=video_id)
		response = self.client.AddVideoEntryToFavorites(video_entry)
		return response

	def RetrieveContactFeedByUri(self, uri):
		feed = self.client.GetYouTubeContactFeed(uri)
		return feed

	def RetrieveContactFeedByUsername(self, username):
		feed = self.client.GetYouTubeContactFeed(username=username)
		return feed

if __name__ == '__main__':
	yt_service = YouTubeService()
	feed = yt_service.RetrieveUserVideosbyUsername('huynhlv54')	
	print getHtmlFeedDescription(feed)
	
