import mysql.connector
from datetime import datetime
import re
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pymongo import MongoClient

from channel_data import *
from queries import *
from server_details import *

def get_channel_data_from_ID(youtube):
    stored_mysql = False
    # Initialize session state variables
    if 'channel_data' not in st.session_state:
        st.session_state.channel_data = {}
    if 'all_comments_data' not in st.session_state:
        st.session_state.all_comments_data = []
    if 'all_playlists_data' not in st.session_state:
        st.session_state.all_playlists_data = []
    if 'all_videos_data' not in st.session_state:
        st.session_state.all_videos_data = []
    if 'channel_id' not in st.session_state:
        st.session_state.channel_id = None
    
    # Get channel data from ID
    st.session_state.channel_id = st.text_input("Enter a channel ID to fetch its data", value = 'UCPpzJ0GR8RIr4Bqe8b9zD4A')

    cols = st.columns(3)
    st.session_state.store_mongodb = cols[0].checkbox("Copy to MongoDB?", None, key = 'mongo')   
    st.session_state.store_mysql_db = cols[1].checkbox("Copy to MySQL?", None, key = 'mysql') 
    st.session_state.delete_db = cols[2].checkbox("Delete this data in MongoDB?", None, key='dletedb') 
    if st.button("Search", key='search_channel_data'):
        if st.session_state.channel_id:
            st.session_state.channel_data, st.session_state.all_videos_data, st.session_state.all_comments_data, st.session_state.all_playlists_data = get_channel_data_with_related(st.session_state.youtube, st.session_state.channel_id)
        else:
            st.warning("Error: Channel ID is not associated with any user!")

    #print(st.session_state.all_videos_data)
    # Create dropdown menu for channel data
    if st.session_state.channel_data:
        channel_drop_down = st.selectbox("Select type of data to display:", ["Channel Data", "Comments Data", "Playlists Data", "Videos Data"])
        #print(channel_drop_down, st.session_state.all_videos_data)
        # Display selected data type
        if channel_drop_down == "Channel Data":
            st.write(pd.DataFrame(st.session_state.channel_data))
        elif channel_drop_down == "Comments Data":
            st.write(pd.DataFrame(st.session_state.all_comments_data))
        elif channel_drop_down == "Playlists Data":
            st.write(pd.DataFrame(st.session_state.all_playlists_data))
        elif channel_drop_down == "Videos Data":
            st.write(pd.DataFrame(st.session_state.all_videos_data))


        client = MongoClient(st.session_state.mongoDB_host)
        db = client["youtube_data"]  
    
        #print(st.session_state.channel_data)
        if st.session_state.channel_data:
            save_to_mongodb('channel_data', st.session_state.channel_data, db, 'Channel_Id')
        else:  
            st.warning(f"The table, channel, is empty!")   
            
        # Save comments data
        if st.session_state.all_comments_data is not None:
            save_to_mongodb('comments_data', st.session_state.all_comments_data, db, 'Comment_Id')       
        else:  
            st.warning(f"The table, comment, is empty!")   
            
        # Save playlists data
        if st.session_state.all_playlists_data is not None:
            save_to_mongodb('playlists_data', st.session_state.all_playlists_data, db, 'Playlist_Id')
        else:  
            st.warning(f"The table, playlist, is empty!")     
    
        # Save video data
        if st.session_state.all_videos_data is not None:
            save_to_mongodb('video_data', st.session_state.all_videos_data, db, 'Video_Id')
        else:  
            st.warning(f"The the table, video, is empty!")   
        
        if st.session_state.store_mysql_db and st.session_state.store_mongodb:
            if not stored_mysql:
                migrate_to_mysql(st.session_state.mongoDB_host, st.session_state.localhost, st.session_state.root, st.session_state.passwd)
                stored_mysql = True
                st.success(f"stored all the 4 tables successfully to MySQL!")
            else:
                st.warning(f"You have already store this channel in MySQL!")


def save_to_mongodb(collection_name, data, db, col):
    #st.write(f" database with the value is {data[0][col]}")
    if st.session_state.store_mongodb:
        # if collection_name == 'channel_data':
        #     data = [data]

        # collection = db.collection_name
        # result = collection.find_one({col: str(data[0][col])}) 

        # st.write("result is ", result)
        
        # if result:
        #     st.success(f"The data for this channel, '{collection_name}', exists in MongoDB.")
        #     return True
        # else:
        #     st.success(f"The data for this channel, '{collection_name}', does not exists in MongoDB.")
        #     db[collection_name].insert_many(data)
        #     st.success(f"Stored the table, '{collection_name}', in MongoDB successfully!")       
        #     return False
            
        # Specify the collection
        collection = db[collection_name]
        
        # Iterate over the data
        for document in data:
            # Check if a similar document already exists in the collection
            existing_document = collection.find_one(document)
            if existing_document:
                print(f"Skipping document as it already exists.")
            else:
                # Insert the document into the collection
                collection.insert_one(document)
                print(f"Inserted document.")
        st.success("Data added successfully!")       


def migrate_to_mysql(mongo_host, localhost, username, passwd):
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
    mongo_collection = mongo_db["playlists_data"]
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
    mongo_collection = mongo_db["comments_data"]
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

        #st.write(video_data.get('Duration', 0))
        
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


def header_queries():
    st.markdown("<h2 style='text-align: center; color: yellow;'>Queries part </h2><br><br>", unsafe_allow_html=True)

# Main function
if __name__ == "__main__":
    
    youtube = get_youtube_api_build()
    mysql_host, root, passwd = MySQL_server_details_UI()
    mongo_host = mongoDB_server_details_UI()  

    get_channel_data_from_ID(youtube)  

    header_queries()
    
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






