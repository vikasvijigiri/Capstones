import mysql.connector
import pandas as pd
import streamlit as st
from pymongo import MongoClient
import re





def parse_duration(duration):

    #duration_pattern = re.compile(r'((?PT<hours>\d+?)h)?((?H<minutes>\d+?)m)?((?M<seconds>\d+?)s)?')
    duration_pattern = re.compile(r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    
    match = duration_pattern.match(duration)
    hours = int(match['hours']) if match['hours'] else 0
    minutes = int(match['minutes']) if match['minutes'] else 0
    seconds = int(match['seconds']) if match['seconds'] else 0
    return hours * 3600 + minutes * 60 + seconds #'{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

    



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
        DISTINCT videos.Video_Name AS Video_name, 
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
            DISTINCT ch.Channel_Name,
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
  