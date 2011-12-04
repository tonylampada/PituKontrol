'''
Created on 12/07/2011

@author: Renzo Nuccitelli
'''

def string_to_none(value):
    if value=="":
        return None
    return value


def _give_method_name_to_decorator(decorator):
    def f(method):
        decFunc = decorator(method)
        decFunc.__name__ = method.__name__
        return decFunc
    f.__name__ = decorator.__name__
    return f

@_give_method_name_to_decorator
def not_none_or_empty_str(func):
    def f(value):
        if value is None or value=="":
            return string_to_none(value)
        return func(value)
    return f
    

@not_none_or_empty_str
def string_to_boolean(value):
        value=value.upper()
        return value=="TRUE"
    
@not_none_or_empty_str
def string_to_float(value):
    value=value.replace(".","")
    value=value.replace(",",".")
    try:
        return float(value)
    except:
        return None

@not_none_or_empty_str
def string_to_int(value):
    try:
        return int(value)
    except:
        return None
@not_none_or_empty_str
def remove_br_phone_signs(phone):
    p=""
    for i in range(len(phone)):
        if i!=0 and i!=3 and i!=4 and i!=9:
            p+=phone[i]
        else:
            try:
                int(phone[i])
                p+=phone[i]
            except:
                pass
    return p

@not_none_or_empty_str
def cep(cep):
    p=""
    for i in range(len(cep)):
        if i!=5:
            p+=cep[i]
        else:
            try:
                int(cep[i])
                p+=cep[i]
            except:
                pass
    return p

@not_none_or_empty_str
def string_to_link(link):
    if link.startswith("http://") or link.startswith("https://"):
        return link
    return "http://"+link

        
def composition(*transforms):
    def f(nextTransform,currentTransform):
        return lambda value: currentTransform(nextTransform(value))
    return reduce(f,transforms,lambda value:value)    

