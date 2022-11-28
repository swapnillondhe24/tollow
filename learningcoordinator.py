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

class newStudentIEP(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['schools'
                                                               , 'iep'
                                                               , 'role'
                                                               , 'assessment_request'
                                                               , 'active'
                                                               ,'learning_coordinator'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")
        print(request_json)
        conn = mysql.connect()
        cursor = conn.cursor()
        mysql_query=('''Select count(*) from tollow.user_info as info, tollow.assessment_request as req where 
                                info.iep = %s 
                            and info.assessment_request = %s 
                            and info.school_name = %s
                            and info.role = %s 
                            and info.active = %s
                            and req.learning_coordinator = %s
                            ''',
                       (request_json['iep']
                        , request_json['assessment_request']
                        , request_json['schools']
                        , request_json['role']
                        , request_json['active']
                        , request_json['learning_coordinator']))
        print(mysql_query)
        cursor.execute('''Select count(*) from tollow.user_info as info, tollow.assessment_request as req where 
                                info.iep = %s 
                            and info.assessment_request = %s 
                            and info.school_name = %s
                            and info.role = %s 
                            and info.active = %s
                            and req.learning_coordinator = %s
                            and info.user_id=req.user_id''',
                       (request_json['iep']
                        , request_json['assessment_request']
                        , request_json['schools']
                        , request_json['role']
                        , request_json['active']
                        , request_json['learning_coordinator']))
        record = cursor.fetchone()
        print (record)
        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = []
        record_list.append(record[0])
        result = create_json('success', record_list)
        return result

class studentAssessnment(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['schools'
                                                              , 'role'
                                                              , 'assessment_request'
                                                              , 'active'
                                                              ,'learning_coordinator'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select count(*) from tollow.user_info as info, tollow.assessment_request as req where 
                                assessment_request = %s 
                            and info.school_name = %s
                            and info.role = %s 
                            and info.active = %s
                            and req.learning_coordinator = %s
                            and info.user_id=req.user_id''',
                       (  request_json['assessment_request']
                        , request_json['schools']
                        , request_json['role']
                        , request_json['active']
                        ,request_json['learning_coordinator']))
        record = cursor.fetchone()
        print (record)
        if not record or record[0] == 0:
            return create_json('no records', "no records found")
        record_list = []
        record_list.append(record[0])
        result = create_json('success', record_list)
        return result
        


def create_json(msg, custom_msg) :
    """Function To Create The JSON"""
    response_listing = []
    try :
        result = {}
        if type(custom_msg) != list and type != dict:
            custom_msg = str(custom_msg)
            response_listing.append(custom_msg)

        if codes[msg] :
            if codes[msg] == '200':
                result = {'headers': {'Content-Type': 'application/json'}, 'statusCode': codes[msg], 'body': custom_msg}
            else :
                result = {'headers': {'Content-Type': 'application/json'}, 'statusCode': codes[msg], 'body': custom_msg}
            result = json.dumps(result)
            return result
        if not codes[msg] :
            result = {'headers': {'Content-Type': 'application/json'}, 'statusCode': 'none', 'body': 'incvalid '
                                                                                                     'response code'}
            result = json.dumps(result)
            return result
    except Exception as e:
        msg = 'Invalid Request'
        res = create_json(msg, str(e))
        return res

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

api.add_resource(newStudentIEP, '/studentiepcount/')
api.add_resource(studentAssessnment, '/studentassessmentcount/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
    app.run(debug=True)