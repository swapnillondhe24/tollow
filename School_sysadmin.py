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

mysql = MySQL(app)

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

class userCount(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['schools','role'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")
        print(request_json)
        conn = mysql.connect()
        cursor = conn.cursor()
        
        cursor.execute('''Select count(*) from tollow.user_info as info where 
                             info.school_name = %s
                             and info.role = %s
                            ''',
                       (request_json['schools']
                       ,request_json['role']))
        record = cursor.fetchone()
        print (record)
        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = []
        record_list.append(record[0])
        result = create_json('success', record_list)
        return result



class activeStudent(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['schools'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select count(*) from tollow.user_info as info where 
                            info.school_name = %s
                            and info.active = "yes" 
                            and info.role = "Student" ''',
                       ( request_json['schools']))
        record = cursor.fetchone()
        print (record)
        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = []
        record_list.append(record[0])
        result = create_json('success', record_list)
        return result
        



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

api.add_resource(userCount, '/userCount/')
api.add_resource(activeStudent, '/activeStudent/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011)
    app.run(debug=True)