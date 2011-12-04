'''
Created on 02/02/2011

@author: Renzo Nuccitelli
'''
from google.appengine.api import users

class PrivateMessenger(object):
    def helloTo(self,username="John Doe"):
        
        self.response.out.write( "Hello "+username+". Your  nickname  is: "+users.get_current_user().nickname())
