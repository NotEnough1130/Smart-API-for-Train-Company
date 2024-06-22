## Overview
This project is a Flask-RESTX API designed to improve the passenger experience for Deutsche Bahn, the national railway company of Germany. The API integrates real-time data from the Deutsche Bahn and Gemini APIs to manage railway stops, retrieve operator profiles, and generate tourism guides.

## Purpose
This project is aim as a excisece to connect with real-life APIs (Deutsche Bahn API, Google Gemini API) and create a new API by aggrate data from these 2 existing API.

## Features
- Add Stops: Import and store stop data from the Deutsche Bahn API into a SQLite database.
- Retrieve Stops: Fetch detailed information about a specific stop, including next departures.
- Delete Stops: Remove stop data from the database.
- Update Stops: Modify details of an existing stop.
- Operator Profiles: Retrieve profiles of operators for services departing from a stop within 90 minutes.
- Tourism Guide: Generate a text-based tourism guide for points of interest around selected stops.

## Technologies Used
Backend: Flask, Flask-RESTX
Database: SQLite
APIs: Deutsche Bahn API, Google Gemini API
Language: Python

Deutsche Bahn API: v6.db.transport.rest is a REST API for the public
transportation system in Germany. 
Reference: https://v6.db.transport.rest/

Google Gemini API: Gemini API is a REST API for using Google’s AI Model named
“Gemini”, which is similar to Chat-GPT. In this project I have 
use a Google Account to create an API key and use the key to generate tourism guides.
Reference: https://ai.google.dev/api/python/google/generativeai

## Setup and Installation
1. Clone the Repository:
```bash
git clone git@github.com:NotEnough1130/Smart-API-for-Train-Company.git
cd BreadcrumbsSmart-API-for-Train-Company
```
2. Create a Virtual Environment and Install Dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Set Up Environment Variables:
- Create a .env file in the root directory.
- Add your Google API key for the Gemini API at '.env' file:
```
GEMINI_API_KEY=your_gemini_api_key
```

## Usage
Running the API
```bash
flask run
```

## API Endpoints
Add Stops: 
- Searches for stops using the Deutsche Bahn API, adds new stops to the database, and updates existing ones.
```bash
PUT /stops?query=<query>
```
Retrieve Stop:
- Retrieves information about a specific stop, including optional fields (name, latitude, longitude).
```bash 
GET /stops/<stop_id>?include=<fields>
```
Delete Stop: 
- Deletes a specific stop from the database.
```bash
DELETE /stops/<stop_id>
```
Update Stop: 
- Updates specific fields of a stop.
```bash
PATCH /stops/<stop_id>
```
Operator Profiles: 
- Retrieves operator information for a specific stop, generating content using the Gemini Pro model.
```bash
GET /operator-profiles/<stop_id>
```
Tourism Guide: 
- Generates a tourism guide based on available transportation data and saves it to a text file, which can be downloaded.
```bash
GET /guide
```

## Tourism Guide Output Demo
1.  Run the Program
```
python main.py
```
2. Add Stops to the Database
```
curl -X PUT "http://localhost:8888/stops" -H "Content-Type: application/json" -d '{"query": "hbf"}'
```

3. Generate the Tourism Guide
```
curl -X GET "http://localhost:8888/guide"
```

```
From: Düsseldorf Hbf
To: Köln Hbf
Result: 3
Top result: {'Transportation_Type': 'nationalExpress', 'Transportation_Name': 'ICE 921', 'Platform': 'Departure from platform 5 towards Frankfurt(Main)Hbf', 'Departure_Time': '2024-04-02T03:21:00+02:00', 'Arrival_Time': '2024-04-02T03:44:00+02:00'}
Description_to_Destination: Köln Hauptbahnhof (Cologne Central Station) is a major railway station in Cologne, Germany. It is one of the largest and busiest stations in the country, with over 1,000 trains departing and arriving each day. The station is a hub for regional, national, and international rail services, and is also served by the Cologne Stadtbahn light rail system. Köln Hbf is located in the heart of Cologne, within walking distance of many of the city's main attractions, including the Cologne Cathedral, the Ludwig Museum, and the Cologne Zoo.
```

