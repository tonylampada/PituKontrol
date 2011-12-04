'''
Created on 02/02/2011

@author: Renzo Nuccitelli
'''

class Messenger(object):
    def helloTo(self,username="John Doe"):
        self.response.out.write( "Hello "+username)
