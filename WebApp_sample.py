import json, urllib, datetime, time, traceback
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from hashlib import sha256
from hmac import HMAC
from flask import Flask, render_template, request, Response, jsonify

app = Flask(__name__,
            static_path=None, 
            static_url_path=None, 
            static_folder='static', 
            template_folder='www')

# change to False in production
app.config['DEBUG'] = True

# define Datastore model
class OurProds(ndb.Model):
    time = ndb.IntegerProperty('t')
    price = ndb.FloatProperty('p')
    sku = ndb.StringProperty('k')
    marketplace = ndb.StringProperty('r')
    stock = ndb.IntegerProperty('s')
    pass 

# use the default bucket
GCS_BUCKET = 'GAE-Project-Name.appspot.com'

@app.route('/orders_table', methods = ['GET', 'POST'])
def return_orders_table(no_template = False):
    prodList = []
    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    yesterday = yesterday.strftime("%Y-%m-%dT%H:%M:%S%z")
    
    kwargs = {
        'Status':'pending'
    }
    
    custom_heads = [
                    'CustomerFirstName',
                    'ItemsCount',
                    'OrderNumber',
                    'AddressShipping',
                    'Statuses'
                    ]
    
    if request.method=='POST':
        try:
            custom_heads = request.form.get(['custom_heads'])
            if custom_heads:
                custom_heads = custom_heads.strip().split(',')
            custom_filters = request.form.get(['custom_filters'])
            if custom_filters:
                custom_filters = custom_filters.split(',')
                for custom_filter in custom_filters:
                    key, value = custom_filter.split('=')
                    kwargs[key] = value
        except:
            traceback.print_exc()
            return render_template('base.html',
                            content = "Error in Custom Filters or Headers format",
                            title = "Orders - Error") 
        
    prodList = call_lazada(action = 'GetOrders', 
                            limit = '100',
                            kwargs = kwargs)
    prodList = prodList['SuccessResponse']['Body']['Orders']

    if no_template:
        return HTML_table_from_list_of_dicts(prodList, custom_heads)
    else:
        content = """
        <form action='/orderslist' method='post'>
            <label for="custom_filters">Additional Info</label>
            <input name='custom_filters' placeholder = 'e.g. Limit=500,Offset=100,Status=ready_to_ship,SortBy=created_at,SortDirection=ASC'type='text'>
            
            <label for="custom_heads">Custom Headers</label>
            <input name='custom_heads' placeholder = 'e.g. PaymentMethod,Price,CreatedAt,NationalRegistrationNumber'type='text'>
            
            <input type="submit" value="Submit">
        </form>
        """
        content += HTML_table_from_list_of_dicts(prodList, custom_heads)
    
    return render_template('base.html',
                            content = content,
                            title = "Orders")

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

def update_prods(spider = 'lazada',prodList = []):
    if not prodList:
        return "Empty Product List"
    prods =[]
    for product in prodList:
        if spider =='lazada':
            model = product['Attributes']['model']
            if product['Skus'][0]['special_price']:
                price = product['Skus'][0]['special_price']
            else:
                price = product['Skus'][0]['price']
            qty = int(product['Skus'][0]['quantity'])
        if spider =='qb':
            model = product['ManufacturerPartNumber']
            price = product['SalesPrice']
            qty = int(product['QuantityOnHand'])
        if spider =='plugins':
            model = product['sku']
            if product['sale_price']:
                price = float(product['sale_price'])
            else:
                price = float(product['regular_price'])
            if product['in_stock']=='True':
                qty = 1
            else:
                qty = 0
        
        searchstring = "select * from OurProds where k ='"+ model + "'"
        data = ndb.gql(searchstring).filter(OurProds.marketplace == spider).fetch()
        
        if len(data)>0:
            try:
                if data[0].price != price:
                    data[0].price = price
                    data[0].time = int(time.time())
                    prods.append(data[0])
                if data[0].stock != qty:
                    data[0].stock = qty
                    data[0].time = int(time.time())
                    prods.append(data[0])
            except:
                traceback.print_exc()
        else:
            new_Prod = OurProds(sku = model,
                                price = price,
                                marketplace = spider,
                                time = int(time.time()),
                                stock = qty)
            prods.append(new_Prod)  
        if len(prods) > 10:
            ndb.put_multi_async(prods)      
    if len(prods) > 0:
        ndb.put_multi(prods) 
    
    return 'Done!'