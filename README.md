# AeroGap: Aviation Supply-Demand Analysis

```text
AeroGap is a data-driven intelligence tool designed to identify underserved flight routes. By analyzing live market pricing and flight availability from the Amadeus API, this project identifies "gaps" where high traveler demand meets low flight supply, suggesting potentially profitable new routes for airlines.
```

## Features:

```text
- Live Market Intelligence: Pivots from restricted historical analytics to live "Shopping" data for 2026 travel trends.

- Intelligent City Search: Integrated IATA lookup to resolve city names (e.g., "London") into 3-letter codes (e.g., "LON").

- Multi-Route Comparison: Automated fetching of flight offers across multiple global destinations from a single origin.

- Comprehensive Data Capture: Extracts grand total prices, seat availability, airline carriers, and duration for deep analysis.

- Aviation "Gap" Formula: Framework to identify underserved routes by calculating the Route Feasibility Index (RFI).
```

## Tech Stack:

```text
Language: Python 
API: Amadeus for Developers (Flight Offers Search)
Libraries: pandas, amadeus, python-dotenv
Environment: Virtual Environment (venv)
Visualization: Jupyter Notebooks (Matplotlib/Seaborn)
```

## Project Structure: 

```text
aero-analysis/
├── scripts/            # Python logic for data collection (fetch_traffic.py)
├── data/               # CSV storage for live market prices and seat counts
├── notebooks/          # Jupyter Notebooks for RFI calculations & charts
├── venv/               # Virtual environment for local dependency management
├── .env                # Amadeus API Key & Secret (not committed)
├── .gitignore          # Prevents venv, .env, and large data from being pushed
└── requirements.txt    # Python dependencies (amadeus, pandas, etc.)
```

## Setup & Installation: 
```text
1. Clone the Repo:
  git clone https://github.com/yourusername/aero-analysis.git

2. Install Requirements:
  pip install amadeus pandas python-dotenv

3. Configure API Keys: Create a .env file and add your credentials:
  AMADEUS_KEY=your_api_key_here
  AMADEUS_SECRET=api_secret_here

4. Run the app:
  python scripts/fetch_traffic.py
```

## Analysis Insights:
```text
The AeroGap framework identifies profitable route opportunities using live data:
Supply vs. Demand: Visualizing flight price density against seat availability.
RFI Score: Ranking destinations by a custom index where high prices + low seats = market gap.
Strategic Recommendations: Data-backed evidence for opening new direct flight paths from Bengaluru.
```

