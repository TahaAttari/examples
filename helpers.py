import json, urllib, datetime
from hashlib import sha256
from hmac import HMAC

def HTML_table_from_list_of_dicts(list_of_dicts, args = None):
    if args:
        keys_list = args
    else:
        keys_list = list_of_dicts[0].keys()
    table = "<table><thead>"
    for table_heading in keys_list:
        table += "<th>" + table_heading + "</th>"    
    table += "</thead><tbody>"    
    for each_dict in list_of_dicts:
        row_out = "<tr>"
        for column_name in keys_list:
            try:
                if not each_dict[column_name]:
                    row_out += "<td> None </td>"
                elif isinstance(each_dict[column_name],dict):
                    row_out += "<td>" + ",".join(each_dict[column_name].values()) + "</td>"
                elif isinstance(each_dict[column_name],list):
                    row_out += "<td>" + ",".join(each_dict[column_name]) + "</td>"
                else:
                    row_out += "<td>" + str(each_dict[column_name]) + "</td>"
            except KeyError:
                row_out += "<td> Header Incorrect </td>"
        row_out += "</tr>"
        table += row_out
    table += "</tbody></table>"    
    return table

def call_lazada(action = None, limit = None, offset = None, method = 'GET', kwargs = None):
    # I know I could have passed **kwargs but considering I controlled the input
    # it seemed superfluous
    if not action:
        return {'error':'action not defined'}
    
    baseURI = "https://api.sellercenter.lazada.com.my?"

    parameters = {
      'UserID': 'user@domain.com',
      'Version': '1.0',
      'Action': action,
      'Format':'json',
      'Timestamp': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
       }
    # max 100 for orders
    if limit:
        parameters['Limit']=limit
    # offset = # of skipped results
    if offset:
        parameters['Offset']=offset
    if kwargs:
        parameters = dict(parameters.items() + kwargs.items())
    api_key = 'secret_api_key'
    concatenated = urllib.urlencode(sorted(parameters.items()))
    parameters['Signature'] = HMAC(api_key, concatenated, sha256).hexdigest()

    result_json = urlfetch.fetch(baseURI + urllib.urlencode(sorted(parameters.items())), 
                                deadline = 60, 
                                method = method)

    return json.loads(result_json.content)