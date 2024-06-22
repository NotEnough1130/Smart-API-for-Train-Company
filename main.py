import os
from pathlib import Path

from dotenv import load_dotenv          
import google.generativeai as genai     
from flask import Flask, send_file, request
from flask_restx import Api, Resource, Namespace, reqparse, abort, fields
from flask_sqlalchemy import SQLAlchemy
from requests import get, RequestException
from datetime import datetime
from socket import gethostbyname, gethostname

appname = Path(__file__).stem        
db_file   = f"{appname}.db"          
txt_file  = f"{appname}.txt"         

# Load the environment variables from the .env file
load_dotenv()

# Configure the API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Create a Gemini Pro model
gemini = genai.GenerativeModel("gemini-pro")

PORT = 8888
HOST_NAME = gethostbyname(gethostname())
app = Flask(__name__)
api = Api(app, title="apiapp", description="API app")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///${db_file}"
db = SQLAlchemy(app)



class stopsModel(db.Model):
   stop_id = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
   # type = db.Column(db.String(20))
   name = db.Column(db.Text)
   latitude = db.Column(db.Text)
   longitude = db.Column(db.Text)
   last_updated = db.Column(db.Text)
   _links = db.Column(db.String(255))

   def __repr__(self):
       return f"stopsModel(stop_id='{self.stop_id}', name='{self.name}', latitude={self.latitude}, longitude={self.longitude}, last_updated='{self.last_updated}', _links='{self._links}')"
       


class departModel(db.Model):
   trip_id = db.Column(db.String(255), nullable=False, primary_key=True)
   stop_id = db.Column(db.String(20), nullable=False)
   platform = db.Column(db.String(20))
   direction = db.Column(db.String(255))
   operator = db.Column(db.String(255))
   last_updated = db.Column(db.Text)

   def __repr__(self):
      return f'departModel(trip_id={self.trip_id}, stop_id={self.stop_id}, platform={self.platform}, direction={self.direction}, operator= {self.operator}, last_updated={self.last_updated})'
   
#Define data get from reuqest 
q1_args = reqparse.RequestParser()  
q1_args.add_argument("query", type=str, help="Pleae provide a string", required=True)

q2_args = reqparse.RequestParser()
q2_args.add_argument("include", type=str, help="Pleae provide a name, latitude or longitude", required=False)

#Define namespace
stops_ns = Namespace("Part 1: stop's information", description="API for stop stations")
operator_ns = Namespace("Part 2: operator's information", description="API for operators")
guide_ns = Namespace("Part 3: tourism guide's information", description="API for create tourism guide")


api.add_namespace(stops_ns, path="/stops")
api.add_namespace(operator_ns, path="/operator-profiles")
api.add_namespace(guide_ns, path="/guide")

@stops_ns.route("")
class stop(Resource):  
   @api.doc(params={'query': "A keyword for search on Deutsche Bahn API and put those results into our database"})
   def put(self):
      exist_flag = False  
      args = q1_args.parse_args()
      url = "https://v6.db.transport.rest/locations"
      params = {
         "query": f"{args["query"]}",
         "results": "5",
      }
      headers = {"accept": "application/json"}
      try:
         response = get(url, params=params, headers=headers)
         data_set = response.json()
      except RequestException as e:
         abort(503, f"Server not avaliable to get data")
      last_update_header = response.headers.get("date")
      last_update = datetime.strptime(last_update_header, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d-%H:%M:%S")
      result_data = []
      for data in data_set:
         existing_record = stopsModel.query.get(data["id"])
         if not existing_record:
            reocrd = stopsModel(stop_id=data['id'],
                                 name = data['name'],
                                 latitude = data['location']['latitude'],
                                 longitude = data['location']['longitude'],
                                 last_updated = last_update,
                                 _links = f'http://{HOST_NAME}:{PORT}/stops/{data['id']}')
            stop_dict = {
                'stop_id': data['id'],
                'last_updated': last_update,
                '_links': {
                    'self': {
                       "href": f'http://{HOST_NAME}:{PORT}/stops/{data['id']}'
                    },
                }
            }
            result_data.append(stop_dict)
            db.session.add(reocrd)
            db.session.commit()
         else:
            exist_flag=True
            existing_record.name =data['name']
            existing_record.latitude = data['location']['latitude']
            existing_record.longitude = data['location']['longitude']
            existing_record.last_updated = last_update
            db.session.commit()
      if exist_flag == False:
         return  result_data, 201
      else:
         return '', 200
   
   @stops_ns.route("/<string:stop_id>")
   class stop_info(Resource):
      @api.doc(params={"include": "Select display of name, latitude and longitude"})
      def get(self, stop_id):
         #Valide stop_id
         exiting_stop_id = stopsModel.query.with_entities(stopsModel.stop_id).all()
         stop_ids = [stop[0] for stop in exiting_stop_id]
         if not stop_id in stop_ids:
            return f'The stop_id {stop_id} was not found in the database.', 400
         #Valide input
         args = q2_args.parse_args().get('include')
         if not args:
            args_list = ['name', 'latitude', 'longitude']
         else:
            valid_input = {'name', 'latitude', 'longitude'}
            args_list = ''.join(args).strip().split(',')
            for arg in args_list:
               if arg not in valid_input:
                  return 'Invalid query', 400

         url = f"https://v6.db.transport.rest/stops/{stop_id}/departures"
         params = {
         "duration": "120",
            }
         headers = {"accept": "application/json"}
         try:
            response = get(url, params=params, headers=headers)
            data_set = response.json()["departures"]
         except RequestException as e:
            abort(503, f"Server not avaliable to get data")
         last_update_header = response.headers.get("date")
         last_update = datetime.strptime(last_update_header, "%a, %d %b %Y %H:%M:%S %Z").strftime("%Y-%m-%d-%H:%M:%S")

         #Storing new data into database
         for data in data_set:
            existing_record = departModel.query.get(data["tripId"])
            if not existing_record and data["platform"]:
                  record = departModel(trip_id = data['tripId'],
                                       stop_id=data["stop"]["id"],
                                       platform = data["platform"],
                                       direction = data["direction"],
                                       operator = data['line']['operator']['name'],
                                       last_updated = last_update)
                  db.session.add(record)
         db.session.commit()

         records = departModel.query.all()
         if not records:
            abort(404, 'No valid departure record')

         depart_data = departModel.query.first()
         stop_data = stopsModel.query.filter_by(stop_id = stop_id).first()
         previous_stop_data = stopsModel.query.filter(stopsModel.stop_id < stop_data.stop_id).order_by(stopsModel.stop_id.desc()).first()
         next_stop_data = stopsModel.query.filter(stopsModel.stop_id > stop_data.stop_id).first()
            
         result_data = {
               "stop_id": stop_data.stop_id,
               "last_updated": depart_data.last_updated,
         }
         for arg in args_list:
            result_data[arg] = getattr(stop_data, arg, None)
         result_data['next_departure'] = depart_data.platform
         result_data["_links"] = {"self": {
                                    "href": stop_data._links
                                 }}
         if next_stop_data:
            result_data["_links"]["next"] = {"href": next_stop_data._links}
         if previous_stop_data:
            result_data["_links"]["prev"] = {"href": previous_stop_data._links}
         return result_data, 200
   
      def delete(self, stop_id):
         #Valide stop_id
         exiting_stop_id= stopsModel.query.with_entities(stopsModel.stop_id).all()
         stop_ids = [stop[0] for stop in exiting_stop_id]
         if stop_id not in stop_ids:
            error_msg = {
               "message": f"The stop_id {stop_id} was not found in the database.",
               "stop_id": stop_id
            }
            return error_msg, 404
         else:
            stop_to_delete = stopsModel.query.filter_by(stop_id=stop_id).all()
            for delete_stop in stop_to_delete:
               db.session.delete(delete_stop)
            db.session.commit()
            result_msg = {
                  "message": f"The stop_id {stop_id} was removed from the database.",
                  "stop_id": stop_id
               }
            return result_msg, 200
      
      request_body_model = api.model('RequestBody', {
         'name': fields.String(description='Name of the entity', example="Morty's House"),
         'latitude': fields.Float(description='Latitude', example=-33.918859),
         'longitude': fields.Float(description='Longitude', example=151.231034)
      })

      @api.doc(body=request_body_model)
      def patch(self, stop_id):
         data=request.json
         exiting_stop_id = stopsModel.query.with_entities(stopsModel.stop_id).all()
         stop_ids = [stop[0] for stop in exiting_stop_id]
         if stop_id not in stop_ids:
            return f'The stop_id {stop_id} was not found in the database.', 400

         target_stop = stopsModel.query.filter_by(stop_id=stop_id).first()
         for key, value in data.items():
               setattr(target_stop, key, value)
         target_stop.last_updated = datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
         db.session.commit()
         result_data = {
               "stop_id": target_stop.stop_id,
               "last_updated": target_stop.last_updated,
               "_links": {
                  "self": {
                     "href": target_stop._links
                  },
            }
         }
         return result_data, 200

@operator_ns.route("/<string:stop_id>")
class oper_info(Resource):
   def get(self, stop_id):
      target_stop = stopsModel.query.filter_by(stop_id=stop_id).first()
      if not stop_id.isdigit() or len(stop_id)!=7 or not target_stop:
            return '[Bad request] Not a valid stop id' , 400
      target_operators = departModel.query.with_entities(departModel.operator).distinct().limit(5).all()
      result_info_list =[]
      for operator in target_operators:
         gemini_response = gemini.generate_content(f'Tell me something about {operator.operator} in around 100 words').text
         result_info = {
            "stop_id": stop_id,
            "profiles": [
               {
                  "operator_name": operator.operator,
                  "information": gemini_response
               }
            ]
         }
         result_info_list.append(result_info)
      return result_info_list, 200

@guide_ns.route("")
class guide_info(Resource):
   def get (self):
      nb_of_stop = stopsModel.query.count()
      if nb_of_stop < 2:
         return 'No valid transportation can be form',400
      stops= stopsModel.query.with_entities(stopsModel.stop_id).all()
      stop_ids = [stop[0] for stop in stops]
      for i in range(len(stop_ids)):
        for j in range(i + 1, len(stop_ids)):
            url = "https://v6.db.transport.rest/journeys"
            params = {
                "from": stop_ids[i],
                "to": stop_ids[j]
            }
            headers = {"accept": "application/json"}
            try:
                response = get(url, params=params, headers=headers)
                data_set = response.json()
            except RequestException as e:
                return "Server not available to get data", 503
            
            if data_set:
                target_data_object = data_set['journeys'][0]['legs'][0]
                stop_dict = {
                    'From': target_data_object['origin']['name'],
                    'To': target_data_object['destination']['name'],
                    'Result': len(data_set['journeys']),
                    'Top result': {
                        'Transportation_Type': target_data_object['line']['product'],
                        'Transportation_Name': target_data_object['line']['name'],
                        'Platform': f"Departure from platform {target_data_object['departurePlatform']} towards {target_data_object['direction']}",
                        'Departure_Time': target_data_object['departure'],
                        'Arrival_Time': target_data_object['arrival']
                    },
                    "Description_to_Destination": gemini.generate_content(f"Give me an overview of {target_data_object['destination']['name']} in around 50 words as a tourism guide").text
                }
                
                with open(txt_file, 'w') as txt_file_do:
                    for key, value in stop_dict.items():
                        txt_file_do.write(f"{key}: {value}\n")
                
                return send_file(txt_file, as_attachment=True)
    
      return "No valid result found", 404

if __name__ == "__main__":
   with app.app_context():
      db.create_all()
   app.run(port=PORT, debug=True)
