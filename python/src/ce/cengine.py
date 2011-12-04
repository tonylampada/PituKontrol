# -*- coding: utf-8 -*-
'''
Created on 31/01/2011

@author: Renzo Nuccitelli

maind module to allow convetion between URL and Python handlers. 

 The Convention:
 
  Supose a Class handler com.module.Handler containing a method called handle
  
  a URL /com/module/Handler/handle should execute the handle method with no args
  a URL /com/module/Handler/handle/param1 should execute the handle method with param1 as first arg
  a URL /com/module/Handler/handle/param1/param2 should execute the handle method with param1 as first arg and param2 as second
  
   and so on...
  
'''


import urllib
from types import  MethodType, ModuleType
#Defining exceptions
class CEException(Exception):
    def __str__(self):
        return self.msg


class HandlerNotFound(CEException):
    def __init__(self, msg = "webapp-ce did not found a handler for this request"):
        self.msg = msg
        
    

class URLNotFound(CEException):
    def __init__(self, msg = "webapp-ce did not found a URL for this Handler"):
        self.msg = msg

#Utilities methods
def path_to_handler(path):
    """
    Used to allow the convention presented on handle module doc
    Returns a Tuple containing the RequestHandlerClass as first item,
    the method name to be executed on the second item 
    and the parameters as a list on last item
    Raises HandlerNotFound Exception if no handler is found
    """
    decoded_path = urllib.unquote(path)
    path_slices = filter(lambda d: d != "", decoded_path.split("/"))
    params = []
    requestHandler = None
    requestHandlerMethod = None

    while len(path_slices) > 0 :
        module_name = ".".join(path_slices)
        try:
            module = __import__(module_name)
            submodule_names = module_name.split(".")[1:]
            for sub in submodule_names:
                module = getattr(module, sub)
            if len(params) >= 2:
                requestHandler = getattr(module, params.pop())
                requestHandlerMethod = getattr(requestHandler, params.pop())
            break
        except ImportError:
            params.append(urllib.quote(path_slices.pop()))
        except AttributeError:
            break
    params.reverse()
    if requestHandler == None or requestHandlerMethod == None:
        raise  HandlerNotFound("Handler not found for path: " + decoded_path)
    return (requestHandler, requestHandlerMethod.__name__, params)

def request_to_handler(request):
    """
    Used to allow the convention presented on handle module doc
    Returns a Tuple containing the RequestHandlerClass as first item,
    the method name to be executed on the second item 
    and the parameters as a list on last item
    Raises HandlerNotFound Exception if no handler is found
    """
    decoded_path = urllib.unquote(request.path)
    path_slices = filter(lambda d: d != "", decoded_path.split("/"))
    params = {}
    requestHandler = None
    requestHandlerMethod = None
    module_name = ".".join(path_slices[0:len(path_slices)-2])
    module = __import__(module_name)
    submodule_names = module_name.split(".")[1:]
    for sub in submodule_names:
        module = getattr(module, sub)

    requestHandler = getattr(module, path_slices[len(path_slices) - 2])
    requestHandlerMethod = getattr(requestHandler, path_slices[len(path_slices) - 1])
    for pname in request.arguments():
        plist=request.get_all(pname)
        if(len(plist) > 1):
            params[pname] = plist
        elif(len(plist) == 1):
            params[pname] = plist[0]
        else:
            params[pname] = None
    if requestHandler == None or requestHandlerMethod == None:
        raise  HandlerNotFound("Handler not found for path: " + decoded_path)
    
    return (requestHandler, requestHandlerMethod.__name__, params)

def handler_to_path(handler,*args):
    """
    Used to be used as the inverse functio from path_to_handler
    Given a handler, returns the url follow the convetion present on handler module doc
    Raises URLNotFound if its impossible to determine the URL
    handler must be a a method class, a class or a module
    """
    params=""
    if args:
        params="/"+"/".join(args)
    if handler != None:
        if isinstance(handler, MethodType):
            return   extract_full_module(handler.im_class) + "/" + handler.__name__+params
        elif isinstance(handler, ModuleType):
            return "/" + handler.__name__.replace(".", "/")+params
        else:
            return extract_full_module(handler)+params
    raise URLNotFound("webapp-ce did not foud a URL for handler: " + handler)

def extract_full_module(klass):
    return "/" + (klass.__module__ + "/" + klass.__name__).replace(".", "/")
