'''
Created on 04/12/2011

@author: p2d
'''
import unittest

class SomeClass():
    def someMethod(self, a, b, c):
        print("self = ",self)
        print("a = ", a)
        print("b = ", b)
        print("c = ", c)

class TestMethodParams(unittest.TestCase):
    def testparametroNormal(self):
        sc = SomeClass()
        sc.someMethod(1, 'dois', 3)

    def testparametroReflect(self):
        x = {}
        x["b"] = "dois"
        x["c"] = 3
        x["a"] = 1
        sc = SomeClass();
        sc.someMethod(**x)
        
