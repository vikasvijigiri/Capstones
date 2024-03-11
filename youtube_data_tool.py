import mysql.connector
from datetime import datetime
import re
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient

#############################################################################################################
#                          Youter user searcher 
#############################################################################################################
def search_channels(youtube, keyword):
    # Build the YouTube API client

    # Search for channels
    request = youtube.search().list(
        q=keyword,
        part='snippet',
        type='channel',
        maxResults=10  # Number of search results to retrieve, adjust as needed
    )
    response = request.execute()

    # Display the search results
    st.header("Channels Found:")
    for item in response['items']:
        st.write(f"Channel Name: {item['snippet']['title']}, Channel ID: {item['snippet']['channelId']}")

def search_UI(youtube):
    st.markdown("<span style='color: green;'> YouTube Channel Search</span>", unsafe_allow_html=True)     
    keyword = st.text_input("Enter a keyword to search for channels:")

    if st.button("Search"):
        if keyword:
            search_channels(youtube, keyword)
        else:
            st.warning("Please enter a keyword to search for channels.")




############################################################################################################
#                                          Input Details
############################################################################################################




# ONE 
def get_youtube_api_build():
    st.set_page_config(layout="wide")  
    st.markdown("<h1 style='text-align: center; color: blue;'>Welcome to Youtube data migration tool UI</h1><br><br>", unsafe_allow_html=True)
    #st.markdown("#### Enter a valid YouTube v3 API key (Public):")    
    st.markdown("<span style='color: green;'> API KEY  (Note: Default is entered below, change accordingly!) </span>", unsafe_allow_html=True)    
    # Text input for API_KEY
    API_KEY = st.text_input("Enter your YouTube API Key", value='AIzaSyBspXWkOgc9y0HNQIUVjMU8oaqgV1HXmMc')
    if not API_KEY:
        st.warning("Please enter your YouTube API Key.")        
    else:    
        youtube = build('youtube', 'v3', developerKey=API_KEY)    
    st.write("---")   
    return youtube

# TWO
def MySQL_server_details_UI():
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            color: green;
        }
        </style>
        """,
        unsafe_allow_html=True
    )      

    st.markdown("<span style='color: green;'> Enter your MySQL server details (Note: Default is entered below, change accordinly!)</span>", unsafe_allow_html=True)    
    

    localhost = st.text_input("Enter hostname", value='localhost')  
    root = st.text_input("Enter username", value='root')
    passwd = st.text_input("Password", value='Vikas@123')   
    return localhost, root, passwd

# Three
def mongoDB_server_details_UI():
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            color: green;
        }
        </style>
        """,
        unsafe_allow_html=True
    )      
    st.markdown("<span style='color: green;'> Enter your MongoDB hostname Note: Default is entered below, change accordingly!</span>", unsafe_allow_html=True)    
    

    mongoDB_host = st.text_input("Enter hostname", value='mongodb://localhost:27017/')  
    st.write("---")
    return mongoDB_host
        

#########################################################################################################
#                                Fetch details from API
#########################################################################################################

def get_channel_data_with_related(youtube, channel_id):
    try:
        channels_data = []
        all_comments_data = []
        all_playlists_data = []
        all_video_data = []

        # Get channel details
        channel_response = youtube.channels().list(
            part='snippet,statistics,contentDetails,status',
            id=channel_id
        ).execute()

        channels_data = []
        # Check if the response contains any items
        if 'items' not in channel_response or len(channel_response['items']) == 0:
            print(f"No channel data found for channel ID: {channel_id}")
        else:
            channel_data = channel_response['items'][0]['snippet']
            channel_statistics = channel_response['items'][0]['statistics']
            channel_status = channel_response['items'][0]['status']
            channel_content_details = channel_response['items'][0]['contentDetails']

            # Access the 'privacyStatus' field under 'status'
            channel_privacy_status = channel_status.get('privacyStatus', 'Unknown')
            # Access the 'madeForKids' field under 'status'
            channel_made_for_kids = channel_status.get('madeForKids', 'Unknown')

            channel_data = {
                'Channel_Name': channel_data['title'],
                'Channel_Id': channel_id,
                'Subscription_Count': channel_statistics.get('subscriberCount', 'Unknown'),
                'Channel_Views': channel_statistics.get('viewCount', 'Unknown'),
                'Channel_Description': channel_data.get('description', 'Unknown'),
                'Channel_Status': channel_privacy_status,
                'Channel_type': channel_made_for_kids
            }
            channels_data.append(channel_data)
        # Get playlists, videos, and comments
        playlists_request = youtube.playlists().list(
            part="snippet,contentDetails",
            channelId=channel_id
        )
        playlists_response = playlists_request.execute()

        for playlist_item in playlists_response["items"]:
            playlist_id = playlist_item["id"]
            playlist_name = playlist_item["snippet"]["title"]

            # Get videos in the playlist
            playlist_items_request = youtube.playlistItems().list(
                part="contentDetails",
                playlistId=playlist_id
            )
            playlist_items_response = playlist_items_request.execute()

            video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]

            all_playlists_data.append({
                'Playlist_Name': playlist_name,
                'Playlist_Id': playlist_id,
                'Channel_Id': channel_id,
            })

            for video_id in video_ids:
                video_response = youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=video_id
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
                    'Duration': content_details.get('duration', ''),
                    'Thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
                    'Caption_Status': content_details.get('caption', 'unknown')
                })

                # Fetch comments for the video
                comments_request = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id
                )
                comments_response = comments_request.execute()

                for comment_thread in comments_response["items"]:
                    snippet = comment_thread["snippet"]["topLevelComment"]["snippet"]

                    comment_data = {
                            'Comment_Id': comment_thread['id'],
                            'Video_Id': video_id,
                            'Comment_Text': snippet['textDisplay'],
                            'Comment_Author': snippet['authorDisplayName'],
                            'Comment_Published_Date': snippet['publishedAt']
                    }

                    all_comments_data.append(comment_data)

        print(f"Total number of playlists: {len(all_playlists_data)}")
        print(f"Total number of videos: {len(all_video_data)}")
        print(f"Total number of comments: {len(all_comments_data)}")

        return channels_data, all_comments_data, all_playlists_data, all_video_data

    except Exception as e:
        print(f"Error retrieving data for channel ID: {channel_id} - {e}")
        return None, None, None, None

def save_to_mongodb(collection_name, data, db, replace_db):
    # Drop the collection if it already exists and replace_db is True
    if collection_name in db.list_collection_names() and replace_db:
        db[collection_name].drop()

    # Check if data is not empty and is a list
    if data and isinstance(data, list):
        # Insert the data into the collection
        db[collection_name].insert_many(data)
        st.write(f"Data saved to {collection_name} collection.")
    else:
        #print("Error: Data is empty or not a list.")
        st.write(f"Error: Data is empty or not a list.")


#########################################################################################################
#                                          Display channel(s) data
#########################################################################################################

# Streamlit UI function to display all channels
def display_all_channels(mongo_host):
    
    # Fetch all channels from MongoDB
    mongo_uri = mongo_host  # Update with your MongoDB URI
    client = MongoClient(mongo_uri)
    db = client["youtube_data"]  # Update with your database name
    collection = db["channel_data"]  # Update with your collection name
    
    # Query MongoDB collection to fetch all channels
    channels = collection.find({})
    

  
    
    # Display channel data in a table
    if channels:
        st.write(" All Channels")
        for channel in channels:
            st.write(f"Channel ID: {channel['Channel_Id']}")
            st.write(f"Channel Name: {channel['Channel_Name']}")
            st.write(f"Subscriber Count: {channel['Subscription_Count']}")
            st.write(f"Total Views: {channel['Channel_Views']}")
            st.write(f"Status: {channel['Channel_Status']}")            
            st.write("---")
    else:
        st.write("No channels found in the database.")
    client.close()  # Close MongoDB connection 


def display_channel_data(mongo_host):
    st.markdown("<span style='color: green;'> Verify If the data is stored in DB successfully! </span>", unsafe_allow_html=True)     
    
    # Text input for channel ID
    channel_id = st.text_input("Enter Channel ID (single channel only):")
    
    # Button to trigger data display
    if st.button("Display Data"):
        # You can replace this with your actual function to fetch channel data
        # MongoDB connection settings
        mongo_uri = mongo_host  # Update with your MongoDB URI
        client = MongoClient(mongo_uri)
        db = client["youtube_data"]  # Update with your database name
        collection = db["channel_data"]  # Update with your collection name
        
        # Query MongoDB collection for channel data based on channel ID
        channel_data = collection.find_one({"channel_id": channel_id})
        
      
        if channel_data:
            st.write("### Channel Data")
            st.write(f"Channel ID: {channel_data['Channel_Id']}")
            st.write(f"Channel Name: {channel_data['Channel_Name']}")
            st.write(f"Subscriber Count: {channel_data['Subscription_Count']}")
            st.write(f"Channel Views: {channel_data['Channel_Views']}")
            st.write(f"Status: {channel_data['Channel_Status']}")            
        else:
            st.write("No data found for the provided channel ID.")
        client.close()  # Close MongoDB connection  
    st.write("---")
#########################################################################################################

#########################################################################################################

def get_subscriber_count(youtube, channel_id):
    try:
        # Get channel details
        channel_response = youtube.channels().list(
            part='statistics',
            id=channel_id
        ).execute()

        # Extract subscriber count
        subscriber_count = int(channel_response['items'][0]['statistics']['subscriberCount'])
        return subscriber_count

    except Exception as e:
        print(f"Error retrieving subscriber count for channel ID {channel_id}: {e}")
        return None

def get_random_channel_ids(youtube, subscriber_lower_lim, subscriber_upper_lim):
    try:
        channel_ids = []

        # Get a large number of channel IDs from YouTube API
        next_page_token = None
        while len(channel_ids) < 10:  # Fetch until we have 10 channel IDs
            channels_response = youtube.search().list(
                part='snippet',
                type='channel',
                maxResults=50,  # Maximum number of channels per page
                pageToken=next_page_token
            ).execute()

            # Iterate through each channel and extract channel ID
            for item in channels_response.get("items", []):
                channel_id = item['id']['channelId']
                subscriber_count = get_subscriber_count(youtube, channel_id)
                if subscriber_count > subscriber_lower_lim and subscriber_count < subscriber_upper_lim:
                    channel_ids.append(channel_id)
                    if len(channel_ids) == 10:
                        break  # Exit the loop once we have 10 channel IDs

            # Check if there are more pages of channels
            next_page_token = channels_response.get('nextPageToken')
            if not next_page_token:
                break  # No more pages available

        return channel_ids

    except Exception as e:
        print(f"Error retrieving random channel IDs: {e}")
        return None




def fetch_subscribers_button(youtube, subscriber_count_lower_limit, subscriber_count_upper_limit):
    if subscriber_count_lower_limit > subscriber_count_upper_limit:
        st.error("Subscriber count lower limit must be less than or equal to the upper limit.")
        return None
    else:
        # Fetch random channel IDs within the specified subscriber count range
        channel_ids_list = get_random_channel_ids(youtube, subscriber_count_lower_limit, subscriber_count_upper_limit)
        return channel_ids_list



def fetch_channel_interface(youtube):
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            color: green;
        }
        </style>
        """,
        unsafe_allow_html=True
    )      
    st.markdown("<span style='color: green;'> 1. Search 10 channels by number subscribers (Result: Fetched channel Id's will be entered automatically in the next section as input) </span>", unsafe_allow_html=True)    
 


    # Subscriber count range
    subscriber_count_lower_limit = st.number_input("Subscriber Count Lower Limit", min_value=100)
    subscriber_count_upper_limit = st.number_input("Subscriber Count Upper Limit", min_value=10000)



    # Button to fetch data
    col1, col2, col3 = st.columns([3, 2, 2])
    with col2:
        # Fetch Subscribers button
        if st.button("Search "):
            channel_ids_list = fetch_subscribers_button(youtube, subscriber_count_lower_limit, subscriber_count_upper_limit)
            if len(channel_ids_list) == 10:
                st.write("<span style='color: green;'>Success: Found 10 channels!</span>", unsafe_allow_html=True)
                for channel_id in channel_ids_list:
                    st.write(f"<span style='color: green; white-space: nowrap;'>Id: '{channel_id}' !</span>", unsafe_allow_html=True)
                return channel_ids_list
    st.write("---")


def fetch_data_interface(youtube, mongo_host, channels_ids_list):
    #st.set_page_config(layout="wide") 
    st.markdown(
        """
        <style>
        .title {
            text-align: center;
            color: green;
        }
        </style>
        """,
        unsafe_allow_html=True
    )      
    st.markdown("<span style='color: green;'> Fetch channel data by Id's found above </span>", unsafe_allow_html=True)    



    # Text input for channel IDs
    channel_input = st.text_area("Enter comma-separated Channel IDs (Multiple channels)", value=channels_ids_list)
    replace_db = st.checkbox("Store it to database?", True)
    


    # Button to fetch data
    col1, col2, col3 = st.columns([3, 2, 2])
    with col2:
        # Fetch Subscribers button
        
        if st.button("Fetch Data from youtube"):
                # Split comma-separated channel IDs
                # if len(channels_ids_list) == 1:
                #     channel_ids_list = []
                #     channel_ids_list.append(channels_ids_list)
                # channel_ids_list = [channel_id.strip() for channel_id in channel_ids.split(",")]
                channels_ids_list = channel_input    

                client = MongoClient(mongo_host)
                db = client["youtube_data"]  
              
                # Call function to fetch data using API_KEY and channel IDs
                for channel_id in channels_ids_list:

                    # Get channel data with related information
                    channel_data, all_comments_data, all_playlists_data, all_videos_data = get_channel_data_with_related(youtube, channel_id)


                    # Save channel data
                    if channel_data is not None:
                        save_to_mongodb('channel_data', channel_data, db, replace_db)
                    
                    # Save comments data
                    if all_comments_data is not None:
                        save_to_mongodb('comments_data', all_comments_data, db, replace_db)
                
                    # Save playlists data
                    if all_playlists_data is not None:
                        save_to_mongodb('playlists_data', all_playlists_data, db, replace_db)

                    # Save video data
                    if all_videos_data is not None:
                        save_to_mongodb('video_data', all_videos_data, db, replace_db)
    # with col3:
    #     if st.button("View already Fetched Data"):

def MySQL_transfer_UI(mongo_host):
    # Streamlit UI
    
    if st.button('Transfer Data'):
        migrate_to_mysql(mongo_host)
        st.success('Data transfer completed successfully!')

def migrate_to_mysql(mongo_host):
    # Connect to MongoDB
    mongo_client = MongoClient(mongo_host)
    mongo_db = mongo_client["youtube_data"]


    
    mongo_collection = mongo_db["channel_data"]
    channel_data_cursor = mongo_collection.find({})
    
    # Connect to MySQL
    mysql_conn = mysql.connector.connect(
        host=localhost,
        user=username,
        password=passwd
    )
    mysql_cursor = mysql_conn.cursor()
    
    # Create MySQL database if not exists
    mysql_cursor.execute("CREATE DATABASE IF NOT EXISTS youtube_data")
    mysql_cursor.execute("USE youtube_data")
    
    # Create MySQL table if not exists
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Channel (
        Channel_Name VARCHAR(255),
        Channel_Id VARCHAR(255),
        Channel_Type VARCHAR(255),
        Channel_Views BIGINT,
        Channel_Description TEXT,
        Channel_Status VARCHAR(255)
    )
    """)
    mysql_conn.commit()
    
    # Iterate over MongoDB cursor and insert data into MySQL table
    for channel_data in channel_data_cursor:
        mysql_cursor.execute("""
        INSERT INTO Channel
        (Channel_Id, Channel_Name, Channel_Type, Channel_Views, Channel_Description, Channel_Status)
        VALUES
        (%s, %s, %s, %s, %s, %s)
        """, (
            channel_data.get('Channel_Id', ''),
            channel_data.get('Channel_Name', ''),
            channel_data.get('Channel_Type', ''),
            channel_data.get('Channel_Views', 0),
            channel_data.get('Channel_Description', ''),
            channel_data.get('Channel_Status', '')
        ))
        mysql_conn.commit()

     # Retrieve all documents from the "playlist_data" collection in MongoDB
    mongo_collection = mongo_db["playlist_data"]
    playlist_data_cursor = mongo_collection.find({})
    
    # Create MySQL table if not exists
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Playlist (
        Playlist_Id VARCHAR(255),
        Channel_Id VARCHAR(255),
        Playlist_Name VARCHAR(255)
    )
    """)
    mysql_conn.commit()
    
    # Iterate over MongoDB cursor and insert data into MySQL table
    for playlist_data in playlist_data_cursor:
        mysql_cursor.execute("""
        INSERT INTO Playlist
        (Playlist_Id, Channel_Id, Playlist_Name)
        VALUES
        (%s, %s, %s)
        """, (
            playlist_data.get('Playlist_Id', ''),
            playlist_data.get('Channel_Id', ''),
            playlist_data.get('Playlist_Name', '')
        ))
        mysql_conn.commit()
    
    
     

    # Retrieve all documents from the "comment_data" collection in MongoDB
    mongo_collection = mongo_db["comment_data"]
    comment_data_cursor = mongo_collection.find({})




    
    
    # Create MySQL table if not exists
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Comment (
        Comment_Id VARCHAR(255),
        Video_Id VARCHAR(255),
        Comment_Text TEXT,
        Comment_Author VARCHAR(255),
        Comment_Published_Date DATETIME
    )
    """)
    mysql_conn.commit()
    
    # Iterate over MongoDB cursor and insert data into MySQL table
    for comment_data in comment_data_cursor:

        comment_published_date_str = comment_data.get('Comment_Published_Date', '')
        # Convert the string to a datetime object
        comment_published_date = datetime.strptime(comment_published_date_str, '%Y-%m-%dT%H:%M:%SZ')
        
        # Format the datetime object as a string in MySQL DATETIME format
        comment_published_date_mysql_format = comment_published_date.strftime('%Y-%m-%d %H:%M:%S')

        
        mysql_cursor.execute("""
        INSERT INTO Comment
        (Comment_Id, Video_Id, Comment_Text, Comment_Author, Comment_Published_Date)
        VALUES
        (%s, %s, %s, %s, %s)
        """, (
            comment_data.get('Comment_Id', ''),
            comment_data.get('Video_Id', ''),
            comment_data.get('Comment_Text', ''),
            comment_data.get('Comment_Author', ''),
            comment_published_date_mysql_format
        ))
        mysql_conn.commit()    


    # Retrieve all documents from the "video_data" collection in MongoDB
    mongo_collection = mongo_db["video_data"]
    video_data_cursor = mongo_collection.find({})
    
    # Create MySQL table if not exists
    mysql_cursor.execute("""
    CREATE TABLE IF NOT EXISTS Video (
        Video_Id VARCHAR(255),
        Playlist_Id VARCHAR(255),
        Video_Name VARCHAR(255),
        Video_Description TEXT,
        Published_Date DATETIME,
        View_Count INT, 
        Like_Count INT, 
        Dislike_Count INT,
        Favorite_Count INT, 
        Comment_Count INT,
        Duration INT,
        Thumbnail VARCHAR(255),
        Caption_Status VARCHAR(255)
    )
    """)
    mysql_conn.commit()
    
    # Iterate over MongoDB cursor and insert data into MySQL table
    for video_data in video_data_cursor:


        video_published_date_str = video_data.get('Published_Date', '')
        # Convert the string to a datetime object
        video_published_date = datetime.strptime(video_published_date_str, '%Y-%m-%dT%H:%M:%SZ')
        
        # Format the datetime object as a string in MySQL DATETIME format
        video_published_date_mysql_format = video_published_date.strftime('%Y-%m-%d %H:%M:%S')

        #print(video_data.get('Duration', 0))
        duration = parse_duration(video_data.get('Duration', 0))

        
        mysql_cursor.execute("""
        INSERT INTO Video
        (Video_Id, Playlist_Id, Video_Name, Video_Description, Published_Date, View_Count, Like_Count, Dislike_Count, 
                    Favorite_Count, Comment_Count, Duration, Thumbnail, Caption_Status)
        VALUES
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            video_data.get('Video_Id', ''),
            video_data.get('Playlist_Id', ''),
            video_data.get('Video_Name', ''),
            video_data.get('Video_Description', ''),
            video_published_date_mysql_format, 
            video_data.get('View_Count', 0),
            video_data.get('Like_Count', 0),
            video_data.get('Dislike_Count', 0),
            video_data.get('Favorite_Count', 0),
            video_data.get('Comment_Count', 0),
            duration,
            video_data.get('Thumbnail', ''),
            video_data.get('Caption_Status', '')
        ))
        mysql_conn.commit()
    # Close connections
    mysql_cursor.close()
    mysql_conn.close()
    mongo_client.close()



def execute_query(query, localhost, root, passwd):
    # Connect to MySQL
    mysql_conn = mysql.connector.connect(
        host=localhost,
        user=root,
        password=passwd,
        database="youtube_data"
    )
    mysql_cursor = mysql_conn.cursor()

    # Execute query
    mysql_cursor.execute(query)

    # Fetch result
    result = mysql_cursor.fetchall()

    # Get column names
    columns = [i[0] for i in mysql_cursor.description]

    # Close connections
    mysql_cursor.close()
    mysql_conn.close()

    # Convert result to DataFrame
    df = pd.DataFrame(result, columns=columns)
    return df


def query1_UI(localhost, root, passwd): 
    # Centering the button text
    st.markdown("<span style='color: green;'> Answer the questions by querying from MySQL  </span>", unsafe_allow_html=True)    

    query = """
    SELECT 
        videos.Video_Name AS Video_name, 
        playlists.Channel_Id AS channel_id
    FROM 
        youtube_data.Video as videos, 
        youtube_data.Playlist as playlists
    WHERE 
        playlists.Playlist_Id = videos.Playlist_Id
    """
    #st.code(query, language='sql') 
    sql_query_input = st.text_area("Q1. Enter your SQL query here:", height=200, value = query)
    
    if st.button("Click to View names of all videos and their channel IDs"): 
        # SQL query to get names of all the videos and their corresponding channels

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size



def query2_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT 
            ch.Channel_Name,
            channel.Views 
        FROM    
            (SELECT 
                pl.Channel_Id AS Channel_Id,
                SUM(vi.View_Count) AS Views
            FROM 
                youtube_data.Video as vi
            JOIN
                youtube_data.Playlist as pl ON pl.Playlist_Id = vi.Playlist_Id 
            GROUP BY
                pl.Channel_Id
            ORDER BY
                Views DESC) AS channel
        JOIN
            youtube_data.Channel  AS ch ON ch.Channel_Id = channel.Channel_Id
        ORDER BY
            Views DESC

    """  
    sql_query_input = st.text_area("Q2. Enter your SQL query here:", height=200, value = query)
    
    if st.button("Channels and their views ", key='query2'): 
        

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size

def query3_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT 
            v.Video_Name AS Video_Name,
            v.View_Count AS Views,
            c.Channel_Name AS Channel_Name
        FROM 
            youtube_data.Video AS v
        JOIN 
            youtube_data.Playlist AS p ON v.Playlist_Id = p.Playlist_Id
        JOIN 
            youtube_data.Channel AS c ON p.Channel_Id = c.Channel_Id
        ORDER BY 
            v.View_Count DESC
        LIMIT 10;
    """
    sql_query_input = st.text_area("Q3. Enter your SQL query here:", height=200, value = query)
    
    if st.button("Top 10 Highest viewed videos and their names "): 
        

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size

def query4_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT 
            vi.Video_Name,
            COUNT(cm.Comment_Id) AS Comment_Count
        FROM 
            youtube_data.Video AS vi
        JOIN 
            youtube_data.Comment AS cm ON cm.Video_Id = vi.Video_Id
        GROUP BY 
            vi.Video_Name;
    """  
    
    sql_query_input = st.text_area("Q4. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Total Comments on the video "): 
    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size

def query5_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT 
            vi.Video_Name,
            ch.Channel_Name,
            vi.Like_Count
        FROM 
            youtube_data.Video AS vi
        JOIN 
            youtube_data.Playlist AS pl ON pl.Playlist_Id = vi.Playlist_Id
        JOIN 
            youtube_data.Channel AS ch ON ch.Channel_Id = pl.Channel_Id
        ORDER BY 
            vi.Like_Count DESC
        LIMIT 10;
    """    
    sql_query_input = st.text_area("Q5. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Videos with highest likes "): 
        

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size

def query6_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT 
            vi.Video_Name,
            SUM(vi.Like_Count) AS Total_Likes,
            SUM(vi.Dislike_Count) AS Total_Dislikes
        FROM 
            youtube_data.Video AS vi
        JOIN 
            youtube_data.Playlist AS pl ON pl.Playlist_Id = vi.Playlist_Id
        JOIN 
            youtube_data.Channel AS ch ON ch.Channel_Id = pl.Channel_Id
        GROUP BY 
            vi.Video_Name;
    """    
    sql_query_input = st.text_area("Q6. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Total Number of likes and dislikes! "): 
        

        # st.header('SQL Query:')
        # st.code(sql_query, language='sql')   
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size


def query7_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT 
            ch.Channel_Name,
            SUM(vi.View_Count) AS Total_Views
        FROM 
            youtube_data.Video AS vi
        JOIN 
            youtube_data.Playlist AS pl ON pl.Playlist_Id = vi.Playlist_Id
        JOIN 
            youtube_data.Channel AS ch ON ch.Channel_Id = pl.Channel_Id
        GROUP BY 
            ch.Channel_Name;
    """
    
    sql_query_input = st.text_area("Q7. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Total number of views and channel Names "): 
        

        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size


def query8_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT DISTINCT
            ch.Channel_Name
        FROM 
            youtube_data.Channel AS ch
        JOIN 
            youtube_data.Playlist AS pl ON pl.Channel_Id = ch.Channel_Id
        JOIN 
            youtube_data.Video AS vi ON vi.Playlist_Id = pl.Playlist_Id
        WHERE 
            YEAR(vi.Published_Date) = 2022;
    """    
    sql_query_input = st.text_area("Q8. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Videos published in 2022 "): 
        

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size


def query9_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT
            ch.Channel_Name,
            AVG(TIME_TO_SEC(TIMEDIFF(
                STR_TO_DATE(SUBSTRING(vi.Duration, 3), '%H:%i:%s'),
                '00:00:00'
            ))) AS Average_Duration_Seconds
        FROM 
            youtube_data.Channel AS ch
        JOIN 
            youtube_data.Playlist AS pl ON pl.Channel_Id = ch.Channel_Id
        JOIN 
            youtube_data.Video AS vi ON vi.Playlist_Id = pl.Playlist_Id
        GROUP BY 
            ch.Channel_Name;
    """    
    sql_query_input = st.text_area("Q9. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Avg duration of videos "): 
        

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size


def query10_UI(localhost, root, passwd):
    
    # Centering the button text
    st.markdown(
        """
        <style>
        .css-1v8v5ot button {
            display: block;
            margin: 0 auto;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    # SQL query to get names of all the videos and their corresponding channels
    query = """
        SELECT
            ch.Channel_Name,
            vi.Video_Name,
            vi.Comment_Count
        FROM 
            youtube_data.Channel AS ch
        JOIN 
            youtube_data.Playlist AS pl ON pl.Channel_Id = ch.Channel_Id
        JOIN 
            youtube_data.Video AS vi ON vi.Playlist_Id = pl.Playlist_Id
        ORDER BY 
            vi.Comment_Count DESC
        LIMIT 10;
    """    
    sql_query_input = st.text_area("Q10. Enter your SQL query here:", height=200, value = query)
        
    if st.button("Videos with highest comments "): 
        

    
        # Execute query and get result as DataFrame
        result_df = execute_query(sql_query_input, localhost, root, passwd)
    

        # Display result as table
        st.subheader('Names of all the videos and their corresponding channels:')
        st.dataframe(result_df, width=800)  # Set width to maintain its size
        
# # Define your API key
# API_KEY = 'AIzaSyBspXWkOgc9y0HNQIUVjMU8oaqgV1HXmMc'
# channels_list = ['UC-elz6w4sbn_5LB37pJjTRA']
# # Initialize the YouTube API client
# youtube = build('youtube', 'v3', developerKey=API_KEY)


# #channels_list = get_random_channel_ids(youtube)
# for channel_id in channels_list:
#     # channel_data = get_channel_data(youtube, channel_id)
#     # playlist_data = display_playlists_with_video_count(youtube, channel_id)
#     # videos_data = get_all_videos(youtube, channel_id)
#     # comments_data = get_all_comments(youtube, channel_id)
#     channel_data, all_comments_data, all_playlists_data, all_video_data = get_channel_data_with_related(youtube, channel_id)
# #print(len(comments_data))
# #print(channel_data)
# #display_playlists_with_video_count(youtube, channel_id)
# channels_list = ['UCS0eUoU4ZCx1rqIs869-7CA', 
#                  'UCwRzKP4CrsdUY0ZGx8W1bdA', 
#                  'UC0_5XC2QxL5gxfFbK9BhMWQ', 
#                  'UCeWEp60KPquIfF5DdTBC2jw', 
#                  'UCo_D1RYTs6fwqQ5ntuW93Mw', 
#                  'UCkuqUCXmmzIwUT5m2ax0oDg', 
#                  'UC-9-hE72jAJOjKKPsd8ep7A', 
#                  'UC4z38txRwogNrThaQFH-VGQ', 
#                  'UCW5ofX1iEwvLdghlmJfLDGQ', 
#                  'UCnzBWP5HlK5V0Z7yTKZk9zA']

# Main function
if __name__ == "__main__":
    
    youtube = get_youtube_api_build()
    mysql_host, root, passwd = MySQL_server_details_UI()
    mongo_host = mongoDB_server_details_UI()  

    
    #search_UI(youtube)
    channel_ids_list = fetch_channel_interface(youtube)      
    fetch_data_interface(youtube, mongo_host, channel_ids_list)
    
    display_channel_data(mongo_host)
    #display_all_channels(mongo_host)

    query1_UI(mysql_host, root, passwd)
    query2_UI(mysql_host, root, passwd)
    query3_UI(mysql_host, root, passwd)    
    query4_UI(mysql_host, root, passwd)
    query5_UI(mysql_host, root, passwd)     
    query6_UI(mysql_host, root, passwd) 
    query7_UI(mysql_host, root, passwd) 
    query8_UI(mysql_host, root, passwd) 
    query9_UI(mysql_host, root, passwd) 
    query10_UI(mysql_host, root, passwd) 

























# ###############################################################################################

# # Function to get channel data
# def get_channel_data(youtube, channel_id):
#     try:
#         # Get channel details
#         channel_response = youtube.channels().list(
#             part='snippet,statistics,contentDetails,status',
#             id=channel_id
#         ).execute()

#         # Check if the response contains any items
#         if 'items' not in channel_response or len(channel_response['items']) == 0:
#             print(f"No channel data found for channel ID: {channel_id}")
#             return None

#         channel_data = channel_response['items'][0]['snippet']
#         channel_statistics = channel_response['items'][0]['statistics']
#         channel_status = channel_response['items'][0]['status']
#         channel_content_details = channel_response['items'][0]['contentDetails']
        
#         # Access the 'privacyStatus' field under 'status'
#         channel_privacy_status = channel_status.get('privacyStatus', 'Unknown')
#         # Access the 'madeForKids' field under 'status'
#         channel_made_for_kids = channel_status.get('madeForKids', 'Unknown')

#         return {
#             'Channel_Name': channel_data['title'],
#             'Channel_Id': channel_id,
#             'Subscription_Count': channel_statistics.get('subscriberCount', 'Unknown'),
#             'Channel_Views': channel_statistics.get('viewCount', 'Unknown'),
#             'Channel_Description': channel_data.get('description', 'Unknown'),
#             'Channel_Status': channel_privacy_status,
#             'Channel_type': channel_made_for_kids
#         }
#     except Exception as e:
#         print(f"Error retrieving data for channel ID: {channel_id} - {e}")
#         return None


# def display_playlists_with_video_count(youtube, channel_id):
#     playlist_info_list = []

#     try:
#         next_page_token = None

#         while True:
#             # Get playlists for a specific channel
#             playlists_response = youtube.playlists().list(
#                 part='snippet,contentDetails',
#                 channelId=channel_id,
#                 maxResults=50,  # Maximum number of playlists per page
#                 pageToken=next_page_token
#             ).execute()

#             # Iterate through each playlist and fetch playlist items
#             for playlist_item in playlists_response['items']:
#                 playlist_id = playlist_item['id']
#                 playlist_name = playlist_item['snippet']['title']
#                 video_count = int(playlist_item['contentDetails']['itemCount'])

#                 print(f"Playlist: {playlist_name} (Playlist ID: {playlist_id})")
#                 print(f"Number of videos: {video_count}")
#                 print()

#                 # Append playlist info to the playlist_info_list
#                 playlist_info_list.append({
#                     'Playlist_Name': playlist_name,
#                     'Playlist_Id': playlist_id,
#                     'Video_Count': video_count
#                 })

#             next_page_token = playlists_response.get('nextPageToken')
#             if not next_page_token:
#                 break  # No more pages available

#         print(f"Total playlists found: {len(playlist_info_list)}")
#         return playlist_info_list

#     except Exception as e:
#         print(f"Error retrieving playlists for channel ID: {channel_id} - {e}")
#         return None


# def get_all_videos(youtube, channel_id):
#     try:
#         # Initialize an empty list to store all videos
#         all_videos = []
#         next_page_token = None

#         while True:
#             # Get playlist details
#             playlist_response = youtube.playlists().list(
#                 part='snippet',
#                 channelId=channel_id,
#                 maxResults=50,  # Maximum number of playlists per page
#                 pageToken=next_page_token
#             ).execute()

#             # Check if the response contains any items
#             if 'items' not in playlist_response or len(playlist_response['items']) == 0:
#                 print(f"No playlists found for channel ID: {channel_id}")
#                 return None

#             playlists = playlist_response.get('items', [])

#             # Iterate over each playlist and extract the playlist data
#             for playlist in playlists:
#                 playlist_id = playlist['id']
#                 # Get videos in the playlist
#                 playlist_items_response = youtube.playlistItems().list(
#                     part='contentDetails',
#                     playlistId=playlist_id,
#                     maxResults=50  # Maximum number of videos per page
#                 ).execute()

#                 # Extract video IDs from playlist items
#                 video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]

#                 # Get details for each video
#                 for video_id in video_ids:
#                     # Get video details
#                     video_response = youtube.videos().list(
#                         part='snippet,statistics,contentDetails',
#                         id=video_id
#                     ).execute()

#                     if 'items' not in video_response or len(video_response['items']) == 0:
#                         print(f"No video data found for video ID: {video_id}")
#                         continue

#                     video_data = video_response['items'][0]

#                     # Extract relevant information
#                     snippet = video_data['snippet']
#                     statistics = video_data['statistics']
#                     content_details = video_data['contentDetails']

#                     video_info = {
#                         'Video_Id': video_id,
#                         'Playlist_Id': playlist_id,
#                         'Video_Name': snippet.get('title', ''),
#                         'Video_Description': snippet.get('description', ''),
#                         'Published_Date': snippet.get('publishedAt', ''),
#                         'View_Count': statistics.get('viewCount', 0),
#                         'Like_Count': statistics.get('likeCount', 0),
#                         'Dislike_Count': statistics.get('dislikeCount', 0),
#                         'Favorite_Count': statistics.get('favoriteCount', 0),
#                         'Comment_Count': statistics.get('commentCount', 0),
#                         'Duration': content_details.get('duration', ''),
#                         'Thumbnail': snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
#                         'Caption_Status': content_details.get('caption', 'unknown')
#                     }

#                     all_videos.append(video_info)

#             # Check if there's another page of playlists
#             next_page_token = playlist_response.get('nextPageToken')
#             if not next_page_token:
#                 break  # No more pages available

#         print(f"Total number of videos: {len(all_videos)}")
#         return all_videos

#     except Exception as e:
#         print(f"Error retrieving video data for channel ID: {channel_id} - {e}")
#         return None


# def get_all_comments(youtube, channel_id):
#     comments_list = []
#     next_page_token = None

#     try:
#         # Get playlists for the channel
#         playlists_request = youtube.playlists().list(
#             part="snippet",
#             channelId=channel_id,
#             maxResults=50
#         )
#         playlists_response = playlists_request.execute()

#         # Iterate over each playlist
#         for playlist_item in playlists_response["items"]:
#             playlist_id = playlist_item["id"]

#             # Get videos in the playlist
#             playlist_items_request = youtube.playlistItems().list(
#                 part="snippet",
#                 playlistId=playlist_id,
#                 maxResults=50
#             )
#             playlist_items_response = playlist_items_request.execute()

#             # Iterate over each video in the playlist
#             for playlist_video_item in playlist_items_response["items"]:
#                 video_id = playlist_video_item["snippet"]["resourceId"]["videoId"]

#                 try:
#                     # Check if video exists before fetching comments
#                     video_request = youtube.videos().list(
#                         part="snippet",
#                         id=video_id
#                     )
#                     video_response = video_request.execute()

#                     if video_response["items"]:
#                         # Fetch comments for the video
#                         while True:
#                             comments_request = youtube.commentThreads().list(
#                                 part="snippet",
#                                 videoId=video_id,
#                                 maxResults=100,
#                                 pageToken=next_page_token
#                             )
#                             comments_response = comments_request.execute()

#                             for comment_thread in comments_response["items"]:
#                                 snippet = comment_thread["snippet"]["topLevelComment"]["snippet"]

#                                 comment_data = {
#                                     'Comment_Id': comment_thread['id'],
#                                     'Video_Id': video_id,
#                                     'Video_Title': video_response["items"][0]["snippet"]["title"],
#                                     'Comment_Text': snippet['textDisplay'],
#                                     'Comment_Author': snippet['authorDisplayName'],
#                                     'Comment_Published_Date': snippet['publishedAt']
#                                 }

#                                 comments_list.append(comment_data)

#                             next_page_token = comments_response.get('nextPageToken')
#                             if not next_page_token:
#                                 break  # No more pages available for comments

#                     else:
#                         print(f"Video not found: {video_id}")

#                 except HttpError as e:
#                     if e.resp.status == 403 and "commentsDisabled" in e.content.decode("utf-8"):
#                         print(f"Comments are disabled for the video: {video_id}")
#                     else:
#                         raise

#     except Exception as e:
#         print(f"Error retrieving comments for channel ID: {channel_id} - {e}")

#     print(f"Total number of comments: {len(comments_list)}")
#     return comments_list
    