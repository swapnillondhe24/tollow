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
import logging
from commonUtils.commonUtils import create_json, param_verfication


logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)


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
        LOGGER.debug(mysql_query)
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
        LOGGER.debug(mysql_query)
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
        LOGGER.info("Mysql Connection Successful")
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
        



api.add_resource(newStudentIEP, '/studentiepcount/')
api.add_resource(studentAssessnment, '/studentassessmentcount/')
app.add_url_rule('/logging', endpoint='logging_get', methods=['GET'])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)
    LOGGER.info("Server Started")
    app.run(debug=True)