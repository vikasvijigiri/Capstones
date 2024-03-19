# YouTube Data Analysis

## Overview

This repository contains scripts and queries for analyzing YouTube data. The data includes information about videos, channels, likes, dislikes, views, comments, and more.

## Prerequisites

Before running the scripts and queries in this repository, ensure the following prerequisites are met:

### MongoDB Setup:
- Install MongoDB shell  
  [Click to download](https://dev.mongodb.com/downloads/file/?id=525959)
- Install MongoDB Compass GUI  
  [Click to download](https://dev.mongodb.com/downloads/file/?id=525959)
- Set up MongoDB on your system (Add the server bin and the mongosh.exe containing bin into the PATH variables).

### MySQL Setup:
- Install MySQL Workbench version 8.0.36 or higher.  
  [Click to download](https://dev.mysql.com/downloads/file/?id=525167)
- Install MySQL server 8.0.36.  
  [Click to download](https://dev.mysql.com/downloads/file/?id=525167)
- Configure the server. (Leave them default).

### Python Libraries:
- Install required Python libraries using pip:
- `pip install google-api-python-client`
- `pip install pymongo`
- `pip install streamlit`
- `pip install mysql-connector-python`
- `pip install pandas`


## Files

- `main.py`: Consists main formatted code in nice block fashion.
- `channel_data.py`: Module connsisting of functions related to channel data retreiving and storing in MongoDB.
- `queries.py`: Module consisting of functions related to querying the stored data from MySQL server.
- `server_details.py`: Module consisting of functions related to input details like API_KEY, MySQL and MongoDB server details.
- `README.md`: This file providing an overview of the repository and its contents.

## Dependencies

- Python 3.x
- Streamlit App
- Jupyter Notebook (optional)
- SQL connector (if working with extracted data)
- MongoDB client for Python
- Pandas, Matplotlib, Seaborn (optional)

## Usage
- streamlit run main.py

## License

This project is licensed under the MIT License. Feel free to modify and distribute the code for your own purposes.

