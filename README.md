YouTube Data Analysis

Overview

This repository contains scripts and queries for analyzing YouTube data. The data includes information about videos, channels, likes, dislikes, views, comments, and more.

Prerequisites


Before running the scripts and queries in this repository, ensure the following prerequisites are met:

MongoDB Setup:  
&nbsp;&nbsp;Install MongoDB shell
&nbsp;&nbsp;&nbsp;&nbsp;Link to download: [Click to download](https://downloads.mongodb.com/compass/mongosh-2.2.0-win32-x64.zip)
&nbsp;&nbsp;Install MongoDB Compass GUI.  
&nbsp;&nbsp;&nbsp;&nbsp;Link to download: [Click to download](https://downloads.mongodb.com/compass/mongodb-compass-1.42.2-win32-x64.exe)
&nbsp;&nbsp;Set up MongoDB on your system (Add the server bin and the mongosh.exe containing bin into the PATH variables).  


MySQL Setup:  
&nbsp;&nbsp;Install MySQL Workbench version 8.0.36 or higher.  
&nbsp;&nbsp;&nbsp;&nbsp;Link to download: [Click to download](https://dev.mysql.com/downloads/file/?id=525959)  
&nbsp;&nbsp;Install MySQL server 8.0.36.  
&nbsp;&nbsp;&nbsp;&nbsp;Link to download: [Click to download](https://dev.mysql.com/downloads/file/?id=525167)   
&nbsp;&nbsp;Confifure the server. (Leave them default).

Python Libraries:  
&nbsp;&nbsp;Install required Python libraries using pip:  
&nbsp;&nbsp;&nbsp;&nbsp;pip install google-api-python-client  
&nbsp;&nbsp;&nbsp;&nbsp;pip install pymongo  
&nbsp;&nbsp;&nbsp;&nbsp;pip install streamlit  
&nbsp;&nbsp;&nbsp;&nbsp;pip install mysql-connector-python  
&nbsp;&nbsp;&nbsp;&nbsp;pip install pandas



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
