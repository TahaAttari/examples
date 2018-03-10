import datetime, time, traceback
from google.appengine.ext import ndb
from flask import Flask, render_template, request
import helpers as hp

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
        
    prodList = hp.call_lazada(action = 'GetOrders', 
                            limit = '100',
                            kwargs = kwargs)
    prodList = prodList['SuccessResponse']['Body']['Orders']

    if no_template:
        return hp.HTML_table_from_list_of_dicts(prodList, custom_heads)
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
        content += hp.HTML_table_from_list_of_dicts(prodList, custom_heads)
    
    return render_template('base.html',
                            content = content,
                            title = "Orders")


@app.route('/update_prods', methods = ['GET'])
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