YouTube Data Analysis

Overview

This repository contains scripts and queries for analyzing YouTube data. The data includes information about videos, channels, likes, dislikes, views, comments, and more.

Prerequisites

Before running the scripts and queries in this repository, ensure the following prerequisites are met:

    MongoDB Setup:
        Install MongoDB shell and MongoDB Compass GUI.
        Set up MongoDB on your system.

    MySQL Setup:
        Install MySQL Workbench version 8.0.36 or higher.
            Link to download: [https://dev.mysql.com/downloads/file/?id=525959](Click to download)
        Install and configure MySQL server 8.0.36.
            Link to download: [https://dev.mysql.com/downloads/file/?id=525167](Click to download)

    Python Libraries:
        Install required Python libraries using pip:
            pip install google-api-python-client
            pip install pymongo
            pip install streamlit
            pip install mysql-connector-python
            pip install pandas


Files

    youtube_data_tool.py: Consists all the code formatted in nice block fashion.
    README.md: This file providing an overview of the repository and its contents.


Dependencies

    Python 3.x
    Streamlit App
    Jupyter Notebook (optional)
    SQL connector (if working with extracted data)
    MongoDB client for python
    Pandas, Matplotlib, Seaborn (optional)


Usage
  
    streamlit run youtube_data_tool_UI.py    
  

License

This project is licensed under the MIT License. Feel free to modify and distribute the code for your own purposes.
