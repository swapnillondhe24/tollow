import re
import os
import json
from datetime import datetime
from flaskext.mysql import MySQL
from flask import Flask, jsonify
from flask_restful import Resource, Api, reqparse
from flaskext.mysql import MySQL
from flask import request
from flask_cors import CORS
import mysql.connector
from datetime import datetime
from commonUtils.commonUtils import create_json


api = ''
app = Flask(__name__)
api = Api(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'tollow'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

codes = {'info': 'info'
    , 'success': '200'
    , 'invalid request': '400'
    , 'missing environment variables': '400'
    , 'configuration file missing': '400'
    , 'internal error': '500'
    , 'connection error': '501'
    , 'database error': '502'
    , 'incorrect Parameters': '401'
    , 'directory missing' : '400'
    , 'invalid method':'405'
    , 'no Write Permission': '400'
    , 'no records': '404'}

mysql = MySQL(app)

class roleDisplay(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['schools', 'role', 'active'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select email from tollow.user_info where role = %s and school_name = %s and active = %s ''', 
                        ( request_json['role'], request_json['schools'], request_json['active']))
        
        record = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in
                  cursor.fetchall()]

        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = list(record)

        result = create_json('success', record_list)
        return result

class studentAssign(Resource):
    def post(self):
        request_json = request.get_json()
        mandate_param = [ 'email'
                        , 'role'
                        , 'school'
                        , 'coordinator'
                        ]

        for element in mandate_param:
            if element not in request_json:
                return create_json('invalid request', "invalid request")
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            mandata_param_value = []
            for element in mandate_param:
                  mandata_param_value.append(request_json[element])

            cursor.execute('''select count(*) from tollow.user_info where email = %s and role = %s and school_name = %s''',
                           (request_json['email'], request_json['role'], request_json['school'])
                           )
                    
            record = cursor.fetchone()
            #print(record)
            if not record and record[0] == 0:
                return create_json('no records', "no records found")

          

            cursor.execute(''' update tollow.assessment_request set learning_coordinator = %s where email = %s 
                                            ''',  (request_json["coordinator"], request_json["email"]))
            conn.commit()

            cursor.execute('''Select count(*) from tollow.assessment_request where email = %s and learning_coordinator = %s''',
                                        (request_json['email'], request_json['coordinator']))
            record = cursor.fetchone()
            if not record and record[0] == 0:
                return create_json('internal error', "internal error")

            return create_json('success', "Updated Student assignment")
        except Exception as error:
            print(error)


def param_verfication(request_json,request_list):
    """Function To Check the passing parameters"""
    # result = {}
    count = 0
    for param in request_list :
        count+=1
        if param in request_json and request_json[param] :
            pass
        else :
            return 'invalid request'
    return 'success'

api.add_resource(roleDisplay, '/roledisplay/')
api.add_resource(studentAssign, '/assignstudent/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012)
    app.run(debug=True)
