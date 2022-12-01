import json
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


def create_json(msg, custom_msg):
    """Function To Create The JSON"""
    response_listing = []
    try:
        result = {}
        if type(custom_msg) != list and type != dict:
            custom_msg = str(custom_msg)
            response_listing.append(custom_msg)

        if codes[msg]:
            if codes[msg] == '200':
                result = {'headers': {'Content-Type': 'application/json'}, 'statusCode': codes[msg], 'body': custom_msg}
            else:
                result = {'headers': {'Content-Type': 'application/json'}, 'statusCode': codes[msg], 'body': custom_msg}
            result = json.dumps(result)
            return result
        if not codes[msg]:
            result = {'headers': {'Content-Type': 'application/json'}, 'statusCode': 'none', 'body': 'invalid '
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

def listToString(s):
    st = ","
    s = eval(s)
    
    return st.join(s)
