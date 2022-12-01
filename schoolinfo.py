import re
import os
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

class curriculumDisplay(Resource):
    def post(self):
        request_json = request.get_json()

        if request_json and 'curriculum' not in request_json:
            return create_json('invalid request', "invalid request")

        if request_json['curriculum'].upper() != 'ALL':
            return create_json('invalid request', "invalid request")

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute('''Select curriculum_name from tollow.curriculum ''')
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
        print(result)
        return result

class registerSchool(Resource):
    def post(self):
        request_json = request.get_json()
        mandate_param = ['school_name'
                        , 'address'
                        , 'city'
                        , 'state'
                        , 'country'
                        , 'pincode'
                        , 'contact_details'
                        , 'share_data'
                        , 'retention'
                        , 'curriculum_name'
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
            mandate_param.append('creation_date')
            mandata_param_value.append(str(datetime.now()))
            query_value = ', '.join(['%s'] * len(mandata_param_value))

            columns = ', '.join(mandate_param)
            insert_sql = ''' INSERT INTO tollow.school_info (%s) VALUES (%s) ''' % (columns, query_value)
            cursor.execute(insert_sql,mandata_param_value)
            conn.commit()

            cursor.execute("Select count(*) from tollow.school_info where school_name = %s", request_json['school_name'])
            record = cursor.fetchone()

            if not record and record[0] == 0:

                return create_json('internal error', "internal error")
            return create_json('success', "SchoolRegistered")
        except Exception as error:
            print(error)


class addCurriculumcategory(Resource):
    def post(self):
        request_json = request.get_json()
        mandate_param = [
                  'category_name'
                , 'sub_category_name'
                , 'curricullum_name'
                , 'school_name'
                ]

        for element in mandate_param:
            if element not in request_json:
                return create_json('invalid request', "invalid request")
        try:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute('''select curriculum_id from tollow.curriculum where curriculum_name = %s'''
                           ,request_json['curricullum_name'])
            record = cursor.fetchall()
            if not record or record[0] == 0:
                return create_json('invalid request', "no records found")

            del request_json['curricullum_name']
            mandate_param.remove('curricullum_name')
            mandate_param.append('curricullum_id')
            request_json['curricullum_id'] = record[0][0]

            mandata_param_value = []
            for element in mandate_param:
                mandata_param_value.append(request_json[element])
            mandate_param.append('creation_date')
            mandata_param_value.append(str(datetime.now()))
            query_value = ', '.join(['%s'] * len(mandata_param_value))
            columns = ', '.join(mandate_param)

            insert_sql = ''' INSERT INTO tollow.curriculum_category_mapping (%s) VALUES (%s) ''' % (columns, query_value)
            cursor.execute(insert_sql, mandata_param_value)
            conn.commit()

            cursor.execute('''Select count(*) from tollow.curriculum_category_mapping where school_name = %s 
                                                                                     and curricullum_id= %s''',
                            (request_json['school_name'], request_json['curricullum_id']))
            record = cursor.fetchall()
            if not record and record[0] == 0:
                return create_json('internal error', "internal error")

            return create_json('success', "Catalogue Added")
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


api.add_resource(registerSchool, '/registerschool/')
api.add_resource(addCurriculumcategory, '/addcategory/')
api.add_resource(curriculumDisplay, '/curriculumDisplay/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5007)
    app.run(debug=True)
