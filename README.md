##Overview
This project is a Flask-RESTX API designed to improve the passenger experience for Deutsche Bahn, the national railway company of Germany. The API integrates real-time data from the Deutsche Bahn and Gemini APIs to manage railway stops, retrieve operator profiles, and generate tourism guides.

##eatures
Add Stops: Import and store stop data from the Deutsche Bahn API into a SQLite database.
Retrieve Stops: Fetch detailed information about a specific stop, including next departures.
Delete Stops: Remove stop data from the database.
Update Stops: Modify details of an existing stop.
Operator Profiles: Retrieve profiles of operators for services departing from a stop within 90 minutes.
Tourism Guide: Generate a text-based tourism guide for points of interest around selected stops.

###Technologies Used
Backend: Flask, Flask-RESTX
Database: SQLite
APIs: Deutsche Bahn API, Google Gemini API
Language: Python

###API Endpoints
Add Stops: PUT /stops?query=<query>
Retrieve Stop: GET /stops/<stop_id>?include=<fields>
Delete Stop: DELETE /stops/<stop_id>
Update Stop: PATCH /stops/<stop_id>
Operator Profiles: GET /operator-profiles/<stop_id>
Tourism Guide: GET /guide
