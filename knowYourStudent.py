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
from commonUtils.commonUtils import create_json , param_verfication, listToString
from datetime import datetime
import logging
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

# str(datetime.now())

        
class teacherNames(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['school'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")


        conn = mysql.connect()
        cursor = conn.cursor()
        mysql_query = '''Select first_name, last_name, email from tollow.user_info as info where info.school_name = %s and info.role="Teacher"'''
        cursor.execute(mysql_query,(request_json['school']))
        LOGGER.info(mysql_query)
        record = cursor.fetchall()
        if not record:
            LOGGER.info("No records Found")
            return create_json('no records', "no records found")
            
        
        print (record)
        result = create_json('success', record)
        
        conn.close()
        return result

class teacherTagging(Resource):
    def post(self):
        request_json = request.get_json()
        request_verification = param_verfication(request_json, ['teachers'])
        
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")
        
        conn = mysql.connect()
        cursor = conn.cursor()
        
        teachers = listToString(request_json['teachers'])
             
        
        
        update_sql = '''UPDATE tollow.know_your_student SET tag_teacher="%s" WHERE tollow.know_your_student.email = "%s";''' % ( teachers,request_json['email'] )
        cursor.execute(update_sql)
        conn.commit()

        cursor.execute("Select count(*) from tollow.know_your_student where email = %s", request_json['email'])
        record = cursor.fetchone()
        if not record and record[0] == 0:
            return create_json('internal error', "internal error")
            
        return create_json('success', "Teachers Tagged")
        
    
class updateIEP(Resource):
    def post(self):
        request_json = request.get_json()
        mandate_param = ['user_id',
                         'email',
                         'school_name',
                         'assessment_results',
                         'barriers_learning',
                         'review_learning_style',
                         'review_strength',
                         'review_interest',
                         'review_limiting_belief',
                         'review_enabling_belief',
                         'negative_goal',
                         'how_goals_can_be_achieved',
                         'any_concerns',
                         'teachers_can_do_additionally',
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

            mandate_param.append('created_date')
            mandata_param_value.append(str(datetime.now()))
            # query_value = ', '.join(['%s'] * len(mandata_param_value))
            
            strng = ""
            for i in range(len(mandate_param)):
                strng = strng + (str(mandate_param[i])+"="+"'"+str(mandata_param_value[i])+"'"+",")
    
            
            strng = strng[:-1]
            print("String:"+ strng)
            
            update_sql = '''UPDATE tollow.know_your_student SET %s WHERE tollow.know_your_student.email = "%s";''' % (strng, mandata_param_value[1])
            cursor.execute(update_sql)
            conn.commit()

            cursor.execute("Select count(*) from tollow.know_your_student where email = %s", request_json['email'])
            record = cursor.fetchone()
            

            if not record and record[0] == 0:
                return create_json('internal error', "internal error")
            
            return create_json('success', "Know Your Student Registered")
        
        except Exception as error:
            print(error)
        finally:
            conn.close()
    
    
class extractIEP(Resource):
    def post(self):
        request_json = request.get_json()

        request_verification = param_verfication(request_json, ['email'])
        if codes[request_verification] != '200':
            return create_json('invalid request', "invalid request")


        conn = mysql.connect()
        cursor = conn.cursor()
        mysql_query = '''Select * from tollow.know_your_student as kns where kns.email = %s '''
        cursor.execute(mysql_query,(request_json['email']))
        
        record = cursor.fetchone()
        if not record:
            return create_json('no records', "no records found")
        
        print (record)
        result = create_json('success', record)
        
        conn.close()
        return result


api.add_resource(teacherNames, '/teacherNames/')
api.add_resource(teacherTagging, '/teacherTagging/')
api.add_resource(updateIEP, '/updateIEP/')
api.add_resource(extractIEP, '/extractIEP/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013)
    app.run(debug=True)