'''
Created on 04/12/2011

@author: p2d
'''
import unittest
from ce import cengine


class RequestMock():
    path = None
    params = None
    
    def __init__(self, path, params):
        self.path = path
        self.params = params
        
    def arguments(self):
        return self.params.keys()
    
    def get_all(self, name):
        return self.params[name]
    
class TestRequestToHandler(unittest.TestCase):
    def testHappyPath(self):
        req = RequestMock("/priv/pacote/testinho/Testinho/Meu/hello", {'x': ["WORLD!"]})
        (handlerClass, methodName, params) = cengine.request_to_handler(req)
        handler = handlerClass()
        method = getattr(handler, methodName)
        method(**params)
        