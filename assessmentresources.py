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
from commonUtils.commonUtils import create_json , param_verfication
from datetime import datetime


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

mysql = MySQL(app)
codes = {'info': 'info', 
        'success': '200', 
        'invalid request': '400', 
        'missing environment variables': '400', 
        'configuration file missing': '400', 
        'internal error': '500', 
        'connection error': '501', 
        'database error': '502', 
        'incorrect Parameters': '401', 
        'directory missing' : '400', 
        'invalid method':'405', 
        'no Write Permission': '400', 
        'no records': '404'}


        
class studentDetails(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['school','learning_coordinator'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")


        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select 
                            first_name
                          , last_name
                          , class_year
                          , iep
                          , user_id
                          , created_date
                          , disability_category
                        from tollow.assessment_request
                        where user_id In ( select user_id from 
                        tollow.user_info where school_name=%s)
                        and learning_coordinator=%s''',
                        (request_json['school']
                        ,request_json['learning_coordinator'])
                       )
        record = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
        print(record)
        record_dict = {}
        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        for key, val in record[0].items():
            print(val)
            if key == 'created_date':
                record_dict[key] = val.strftime("%d-%m-%Y")
            else:
                record_dict[key] = val
        record_list = [(record_dict)]
        print (record_list)
        result = create_json('success', record_list)
        return result


api.add_resource(studentDetails, '/studentdetails/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)
    app.run(debug=True)