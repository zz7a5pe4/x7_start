import simplejson

class Params( object ):
    data = {}
    
    def __init__(self, form ):        
        self.data['HOST_IP'] = form['HOST_IP']
        self.data['MULTI_HOST'] = form['MULTI_HOST']
        self.data['GLANCE_HOSTPORT'] = form['GLANCE_HOSTPORT']
        
        self.data['FLAT_INTERFACE'] = form['FLAT_INTERFACE']
        self.data['FIXED_RANGE'] = form['FIXED_RANGE']
        self.data['FIXED_NETWORK_SIZE'] = form['FIXED_NETWORK_SIZE']
        self.data['FLOATING_RANGE'] = form['FLOATING_RANGE']
        
        self.data['MYSQL_HOST'] = form['MYSQL_HOST']
        self.data['MYSQL_PASSWORD'] = form['MYSQL_PASSWORD']
        
        self.data['SERVICE_TOKEN'] = form['SERVICE_TOKEN']
        self.data['RABBIT_PASSWORD'] = form['RABBIT_PASSWORD']
        self.data['ADMIN_PASSWORD'] = form['ADMIN_PASSWORD']
    
    def json(self):
        return simplejson.dumps(self.data )      
      
    def is_valid(self):
        return True