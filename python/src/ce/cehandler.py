'''
Created on 02/02/2011

@author: Renzo Nuccitelli
'''

import webapp2
from ce import cengine
from google.appengine.ext.webapp.util import run_wsgi_app


class BaseHandler(webapp2.RequestHandler):
    def get(self):
        self.makeConvetion()
    def post(self):
        self.makeConvetion()
    def makeConvetion(self):
        (handlerClass, methodName, params) = cengine.request_to_handler(self.request)
        handler = handlerClass()
        handler.request = self.request
        handler.get=self.request.get
        handler.write=self.response.out.write
        handler.response = self.response
        handler.handler = self
        handler.redirect=self.redirect
        method = getattr(handler, methodName)
        method(**params)

app = webapp2.WSGIApplication([("/.*", BaseHandler)], debug = True)

def main():
    run_wsgi_app(app)

if __name__ == "__main__":
    main()