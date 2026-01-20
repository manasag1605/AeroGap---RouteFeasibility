# YouTube Analytics Tracker

```text
An automated data pipeline that scrapes YouTube creator data using the YouTube Data API v3, stores daily snapshots in a SQLite database, and visualizes channel growth in Power BI.
- Includes three modes of interaction:
- Automatic Database Refresh (Daily Tracking)
- New Channel Discovery & Management
- Channel Deletion & Database Cleanup
```

## Features:

```text
- Automated Data Pipeline: CLI tool to manage a tracking list of YouTube creators without repeated manual URL entry.

- Daily Snapshots: Captures historical views, likes, comments, and subscriber counts to visualize trends over time.

- CRUD Functionality: Interactive menu to Add new channels, Refresh existing data, or Delete creators from the tracking list.

- Relational Database: Structured SQLite storage using normalized tables for Channels, Videos, and daily Video Statistics.

- Dynamic Dashboard: Professional Power BI report linked to SQL with automated refresh for real-time channel growth analysis.
```

## Tech Stack:

```text
Language: Python 3.x
API: YouTube Data API v3
Database: SQLite
Visualization: Power BI Desktop
Libraries: requests, sqlite3, python-dotenv
```

## Project Structure: 

```text
youtube-analytics/
│── fetch_youtube_data.py       # Main Python logic & CLI menu
│── database.db                 # SQLite database (stores historical stats)
│── .env                        # YouTube API Key (not committed)
│── .gitignore                  # Prevents DB and env files from being pushed
│── requirements.txt            # Python dependencies
└── YouTube_Dashboard.pbix      # Power BI dashboard file
```

## Setup & Installation: 
```text
1. Clone the Repo:
  git clone https://github.com/manasag1605/youtube-analytics.git

2. Install Requirements:
  pip install requests python-dotenv

3. Configure API Key: Creat a .env file and add your key:  
  YOUTUBE_API_KEY=your_api_key_here

4. Run the app:
  python fetch_youtube_data.py
```

## Dashboard Insights:
```text
The Power BI dashboard provides a "YouTube Studio" style experience:
KPI Cards: Total Subscribers, Total Views, Total Videos, and Engagement Rate.
Growth Trend: A line chart showing view count accumulation over time.
Content Leaderboard: A detailed table of videos ranked by viewership and engagement.
```

