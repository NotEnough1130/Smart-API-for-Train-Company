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

## API Endpoints
Add Stops: 
```bash
PUT /stops?query=<query>
```
Retrieve Stop:
```bash 
GET /stops/<stop_id>?include=<fields>
```
Delete Stop: 
```bash
DELETE /stops/<stop_id>
```
Update Stop: 
```bash
PATCH /stops/<stop_id>
```
Operator Profiles: 
```bash
GET /operator-profiles/<stop_id>
```
Tourism Guide: 
```bash
GET /guide
```

##Setup and Installation
1. Clone the Repository:
```bash
git clone https://github.com/yourusername/deutsche-bahn-api.git
cd deutsche-bahn-api
```
2. Create a Virtual Environment and Install Dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
3. Set Up Environment Variables:
- Create a .env file in the root directory.
- Add your Google API key for the Gemini API:
```
GEMINI_API_KEY=your_gemini_api_key
```

## Usage
Running the API
```bash
flask run
```

