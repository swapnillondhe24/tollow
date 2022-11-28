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
cors = CORS(app, resources={r"/*": {"origins": "*"}})
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'tollow'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'

mysql = MySQL(app)

class authenticateuser(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'username' not in request_json:
            return {'Status': 'Invalid Request for username'}
        if request_json and 'password' not in request_json:
            return {'Status': 'Invalid Request for password'}

        if not request_json['username']:
            return {'Status': 'Invalid User Name & Password'}
        if not request_json['password']:
            return {'Status': 'Invalid User Name & Password'}

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select count(*) from tollow.user_info where email=%s && password=%s ''', (request_json['username'], request_json['password']))
        record = cursor.fetchone()

        if record[0] == 0:
            return {'Status': 'Invalid User Name & Password'}
        elif record[0] != 0:
            return {'Status': 'Login Successful'}
        elif not record[0]:
            return {"Status": 'Invalid Request'}

class validateUser(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'username' not in request_json:
            return {'Status' : 'Invalid Request'}

        if not request_json['username']:
            return {'Status' : 'Invalid User Name'}

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select count(*) from tollow.user_info where email=%s ''',
                       (request_json['username']))
        record = cursor.fetchone()

        if record[0] == 0:
            return {'Status': 'Successful'}
        elif record[0] != 0:
            return {'Status': 'Duplicate'}
        elif not record[0]:
            return {'Status': 'Invalid Entry'}

class rolesDisplay(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'roles' not in request_json:
            return {'Status' : 'Invalid Request'}

        if request_json['roles'].upper() != 'ALL':
            return {'Status' : 'Invalid Request'}

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select role_name from tollow.user_role where registration_page=%s ''',
                       ('yes'))
        record = cursor.fetchall()
        if not record:
            return create_json('invalid request', "no records found")
        record_list = []
        for rec in record:
            print({"rec": rec})
            rec = (str(rec).replace(',', ''))
            rec = (str(rec).replace('((', '('))
            rec = (str(rec).replace('))', ')'))

            rec = (str(rec).replace("('", ''))
            rec = (str(rec).replace("')", ''))

            record_list.append(rec)
        result = create_json('success', record_list)
        return result

class schoolsDisplay(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'schools' not in request_json:
            return create_json('invalid request', "invalid request")

        if request_json['schools'].upper() != 'ALL':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select school_name from tollow.school_info where registration_page=%s and active=%s''',
                       ('yes','yes'))
        record = cursor.fetchall()
        if not record:
            return create_json('no records', "no records found")
        record_list = []
        for rec in record:
            rec = (str(rec).replace(',', ''))
            rec = (str(rec).replace('((', '('))
            rec = (str(rec).replace('))', ')'))

            rec = (str(rec).replace("('", ''))
            rec = (str(rec).replace("')", ''))
            
            record_list.append(rec)
        result = create_json('success', record_list)
        return result


class authorizeUser(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'username' not in request_json:
            return create_json('invalid request', "invalid request")

        if not request_json['username']:
            return create_json('invalid request', "values not found")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select first_name, last_name, email, role, school_name,active from tollow.user_info where email=%s ''',
                       request_json['username'])
        record = [dict(line) for line in [zip([column[0] for column in cursor.description], row) for row in cursor.fetchall()]]
        if not record:
            return create_json('no records', "no records found")
        result = create_json('success', record)
        return result

class registerUser(Resource):
    def post(self):
        request_json = request.get_json()
        mandate_param = ['first_name', 'last_name' , 'email', 'password', 'role', 'school_name', 'contact_number', 'class_year', 'date_of_birth', 'address']
        for element in mandate_param:
            if element not in request_json:
                return create_json('invalid request', "invalid request mandatory param")
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            mandata_param_value = []
            for element in mandate_param:
                  mandata_param_value.append(request_json[element])
            mandate_param.append('creation_date')
            mandata_param_value.append(str(datetime.now()))
            query_value = ', '.join(['%s'] * len(mandata_param_value))

            columns = ', '.join(mandate_param)
            
            insert_sql = ''' INSERT INTO tollow.user_info (%s) VALUES (%s) ''' % (columns, query_value)
            cursor.execute(insert_sql,mandata_param_value)
            conn.commit()

            cursor.execute("Select count(*) from tollow.user_info where email = %s", request_json['email'])
            record = cursor.fetchone()
            print(record)
            if not record and record[0] == 0:
                print ("hello")
                return create_json('internal error', "internal error")
            return create_json('success', "UserRegistered")
        except Exception as error:
            print(error)


class studentUpdate(Resource):
    def post(self):
        request_json = request.get_json()
        mandate_param = ['email', 'school', 'active', 'iep', 'assessment_request']

        for element in mandate_param:
            if element not in request_json:
                return create_json('invalid request', "invalid request")
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            mandata_param_value = []
            for element in mandate_param:
                mandata_param_value.append(request_json[element])

            cursor.execute(
                '''select count(*) from tollow.user_info where email = %s and school_name = %s''',
                (request_json['email'], request_json['school'])
                )

            record = cursor.fetchone()
            print(record)
            print (request_json["active"])
            if not record and record[0] == 0:
                return create_json('no records', "no records found")
            update_query = '''update tollow.user_info 
                                SET   active = %s, iep = %s
                                    , assessment_request = %s 
                                where email = %s and school_name = %s'''
            values = ( request_json["active"], request_json["iep"], request_json["assessment_request"], request_json["email"], request_json["school"])
            cursor.execute(update_query, values)
            conn.commit()

            cursor.execute('''Select count(*) from tollow.user_info where email = %s and school_name = %s''',(request_json['email'], request_json['school']))
            record = cursor.fetchall()
            print ("Updated ")
            print (record)

            if not record and record[0] == 0:
                return create_json('internal error', "internal error")

            return create_json('success', "Updated Student assignment")
        except Exception as error:
            print(error)


api.add_resource(authenticateuser, '/authen/')
api.add_resource(validateUser, '/validate/')
api.add_resource(rolesDisplay, '/roles/')
api.add_resource(authorizeUser, '/accessuser/')
api.add_resource(schoolsDisplay, '/schools/')
api.add_resource(registerUser, '/userregistration/')
api.add_resource(studentUpdate, '/studentupdate/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)
    app.run(debug=True)