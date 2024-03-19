import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# def get_videos_from_channel_section(youtube, channel_id, section):
#     videos = []

#     # Get channel sections
#     channel_sections_request = youtube.channelSections().list(
#         part='contentDetails',
#         channelId=channel_id
#     )
#     channel_sections_response = channel_sections_request.execute()

#     for section_item in channel_sections_response['items']:
#         if section_item['snippet']['type'] == 'singlePlaylist' and section_item['snippet']['style'] == section:
#             playlist_id = section_item['contentDetails']['playlists'][0]
#             playlist_items_request = youtube.playlistItems().list(
#                 part='contentDetails',
#                 playlistId=playlist_id
#             )
#             playlist_items_response = playlist_items_request.execute()

#             for item in playlist_items_response['items']:
#                 video_id = item['contentDetails']['videoId']
#                 videos.append(video_id)

#     return videos



def get_channel_data_with_related(youtube, channel_id):
    try:
        # ###########################################################################################
        #                                  PART: Channel Data
        # ###########################################################################################        
        try:
            channels_data = []
    
            # Get channel details
            channel_response = youtube.channels().list(
                part='snippet,statistics,contentDetails,status',
                id=channel_id
            ).execute()
    
            # Check if the response contains any items
            channel_data = channel_response['items'][0]['snippet']
            channel_statistics = channel_response['items'][0]['statistics']
            channel_status = channel_response['items'][0]['status']
            channel_content_details = channel_response['items'][0]['contentDetails']
            channel_privacy_status = channel_status.get('privacyStatus', 'Unknown')
            channel_made_for_kids = channel_status.get('madeForKids', 'Unknown')
            channel_data = {
                'Channel_Name': channel_data.get('title', ''),
                'Channel_Id': channel_id,
                'Subscription_Count': channel_statistics.get('subscriberCount', 'Unknown'),
                'Channel_Views': channel_statistics.get('viewCount', 'Unknown'),
                'Channel_Description': channel_data.get('description', 'Unknown'),
                'Channel_Status': channel_privacy_status,
                'Channel_type': channel_made_for_kids
            }
            channels_data.append(channel_data)
        except HttpError as e:
            if e.resp.status == 403 or e.resp.status == 404:
                st.warning("There is HTTP error in retreiving channel data.... Skipping it!")
                pass
            else:
                st.warning("There is HTTP error in retreiving channel data.... Skipping it!")                
                raise HttpError(e.resp, e.content)

        # ###########################################################################################
        #                          PART: Video Data, Comments, Playlists
        # ###########################################################################################   
        try:
            all_comments_data = []
            all_playlists_data = []
            all_video_data = []    

            # Get all playlists
            next_page_token = None
            while True:
                playlists_request = youtube.playlists().list(
                    part="snippet,contentDetails",
                    channelId=channel_id,
                    pageToken=next_page_token,
                    maxResults = 1000
                )
                playlists_response = playlists_request.execute()
                video_ids_list = []
                playlist_ids_list = []
                for playlist_item in playlists_response["items"]:
                    playlist_id = playlist_item.get("id", '')
                    playlist_name = playlist_item["snippet"].get("title","")
                    all_playlists_data.append({
                        'Playlist_Name': playlist_name,
                        'Playlist_Id': playlist_id,
                        'Channel_Id': channel_id,
                    })
                    
                    # Get videos in the playlist
                    playlist_items_request = youtube.playlistItems().list(
                        part="contentDetails",
                        playlistId=playlist_id,
                        maxResults=1000,
                    )
                    playlist_items_response = playlist_items_request.execute()
                    #print("camer ehre")    
                    video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]
                    #print(playlist_id, video_ids)
                    for video_id in video_ids:                        
                        if video_id not in video_ids_list:
                            video_response = youtube.videos().list(
                                part='snippet,statistics,contentDetails',
                                id=video_id,
                                maxResults=10000,
                            ).execute()
        
                            if 'items' not in video_response or len(video_response['items']) == 0:
                                print(f"No video data found for video ID: {video_id}")
                                continue
        
                            video_data = video_response['items'][0]
        
                            snippet = video_data['snippet']
                            statistics = video_data['statistics']
                            content_details = video_data['contentDetails']
        
                            all_video_data.append({
                                'Video_Id': video_id,
                                'Playlist_Id': playlist_id,
                                'Video_Name': snippet.get('title', ''),
                                'Video_Description': snippet.get('description', ''),
                                'Published_Date': snippet.get('publishedAt', ''),
                                'View_Count': statistics.get('viewCount', 0),
                                'Like_Count': statistics.get('likeCount', 0),
                                'Dislike_Count': statistics.get('dislikeCount', 0),
                                'Favorite_Count': statistics.get('favoriteCount', 0),
                                'Comment_Count': statistics.get('commentCount', 0),
                                'Duration': content_details.get('duration', '')
                                # 'Thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                                # 'Caption_Status': content_details.get('caption', 'unknown')
                            })
                            
                            try:
                                # Fetch comments for the video
                                comments_request = youtube.commentThreads().list(
                                    part="snippet",
                                    videoId=video_id
                                )
                                comments_response = comments_request.execute()
            
                                for comment_thread in comments_response["items"]:
                                    snippet = comment_thread["snippet"]["topLevelComment"]["snippet"]
            
                                    comment_data = {
                                            'Comment_Id': comment_thread.get('id',''),
                                            'Video_Id': video_id,
                                            'Comment_Text': snippet.get('textDisplay',''),
                                            'Comment_Author': snippet.get('authorDisplayName',''),
                                            'Comment_Published_Date': snippet.get('publishedAt', None)
                                    }
            
                                    all_comments_data.append(comment_data)
                            except HttpError as e:
                                if e.resp.status == 403 and 'commentsDisabled' in str(e):
                                    st.warning("There is HTTP error retreiving in comment data.... Skipping it!")
                                    pass
                                else:
                                    raise HttpError(e.resp, e.content)    
                        video_ids_list.append(video_id)  
                    playlist_ids_list.append(playlist_id)
                next_page_token = playlists_response.get("nextPageToken")
                if not next_page_token:
                    break  # No more pages
        except HttpError as e:
            if e.resp.status == 403 or e.resp.status == 404:
                st.warning("There is HTTP error retreiving in video data.... Skipping it!")                
                pass
            else:
                st.warning("There is HTTP error retreiving in video data.... Skipping it!")      
                raise HttpError(e.resp, e.content)                    
        return channels_data, all_video_data, all_comments_data, all_playlists_data

    except HttpError as e:
        st.warning("There is HTTP error.... Skipping it!")
        return None, None, None, None
    except Exception as e:
        st.warning(f"Error: Some unknown error type found - {e}")
        return None, None, None, None





