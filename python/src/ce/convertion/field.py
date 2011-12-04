# -*- coding: utf-8 -*-
'''
Created on 17/03/2011

@author: Renzo Nuccitelli
'''
from google.appengine.ext import db

ERROR_MSGS = {"invalidMail":u"Email inválido", "requiredField":u"Campo Obrigatório",
               "invalidLink":u"Link Inválido", "invalidBrPhone":u"Telefone Inválido. Exemplo válido: (12) 1212-1212",
               "invalidCep":u"CEP Inválido","invalidBoolean":u"Opção Inválida","invalidRealCurrency":u"Moeda Inválida",
               "invalidInt":u"Valor Inválido","invalidChoice":u"Opção Inválida","invalidChoices":u"Opções Inválidas"}


def insertHttpPrefix(webSite):
    if webSite is None or webSite == "":
        return None
    elif not webSite.startswith("http://"):
        return "http://" + webSite
    return webSite


class BaseField(object):
    '''Class to represent a HTML form field
        Subclasses must implement validate() method
        the method must return a empty dict if everything is ok
        otherwise must return a dict containing the property
        name as key and a error message
    '''

    def isEmpty(self, value):
        return not value

    def __init__(self, label, toModelTransform = lambda v: v != u"" and v or None, fromModelTransform = None, required = True, choices = None):
        self.label = label
        self.toModelTransform = toModelTransform
        self.fromModelTransform = fromModelTransform
        self.required = required
        self.choices = choices

    def validate(self, value):
        if self.required and self.isEmpty(value):
            return ERROR_MSGS["requiredField"]
        elif self.isEmpty(value):
            return None
        return self.specValidate(value)

    def specValidate(self, value):
        '''
        This method must be implemented by subclasses
        '''
        raise NotImplementedError("This method must be implemented by subclasses")

    def transformToModel(self, value):
        if self.toModelTransform:
            return self.toModelTransform(value)
        return value


    def transformFromModel(self, modelValue):
        if self.fromModelTransform:
            return self.fromModelTransform(modelValue)
        return modelValue


class RequiredField(BaseField):
    def specValidate(self, value):
        return None
    
    
def _booleanStrTransform(value):
    value=value.upper()
    if value=="TRUE":
        return True
    elif value=="FALSE":
        return False
    
def _toBrYesNo(value):
    if value is None:
        return ""
    return value and "True" or "False"

    
class BooleanField(BaseField):
    def __init__(self, label , toModelTransform = _booleanStrTransform, fromModelTransform = _toBrYesNo, *arg, **kwargs):
        super(BooleanField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)
    
    def specValidate(self, value):
        value=value.upper()
        if value=="TRUE" or value=="FALSE":
            return None
        return ERROR_MSGS["invalidBoolean"]
    
def _toReal(floatNumber):
    if floatNumber is None:
        return ""
    s="%.2f" %floatNumber
    s=s[::-1].replace(".",",")
    num=""
    for i in range(0,len(s)):
        if i>5 and (i%3) == 0 and len(s)>i:
            num="."+num
        num=s[i]+num
    return num

def _toFloat(real):
    real=real.replace(".","")
    real=real.replace(",",".")
    return float(real)
    

class RealCurrencyField(BaseField):
    def __init__(self, label , toModelTransform = _toFloat, fromModelTransform = _toReal, *arg, **kwargs):
        super(RealCurrencyField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)
        
    def specValidate(self, value):
        try:
            self.toModelTransform(value)
        except:
            return ERROR_MSGS["invalidRealCurrency"]
        return None


class IntField(BaseField):
    def __init__(self, label , toModelTransform = lambda i: int(i), fromModelTransform = lambda i:str(i), *arg, **kwargs):
        super(IntField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)
        
    def specValidate(self, value):
        try:
            self.toModelTransform(value)
        except:
            return ERROR_MSGS["invalidInt"]
        return None
    
    
class RadioStringField(BaseField):
    def __init__(self, label , toModelTransform = None, fromModelTransform = None,optLabels=None, *arg, **kwargs):
        super(RadioStringField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)
        self.optLabels=optLabels
        
    def specValidate(self,value):
        if value in self.choices:
            return None
        return ERROR_MSGS["invalidChoice"]
    
    
class MultipleStringField(BaseField):
    def __init__(self, label ,optLabels, toModelTransform = None, fromModelTransform = None, *arg, **kwargs):
        super(MultipleStringField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)
        self.optLabels=optLabels
        
    def specValidate(self,value):
        values=set(value)
        choiceSet=set(self.choices)
        if values.issubset(choiceSet):
            return None
        return ERROR_MSGS["invalidChoices"]
        
    
_rfc822_specials = '()<>@,;:\\"[]'

def _isAddressValid(addr):
    "Copied from http://www.secureprogramming.com/?action=view&feature=recipes&recipeid=1"
    # First we validate the name portion (name@domain)
    c = 0
    while c < len(addr):
        if addr[c] == '"' and (not c or addr[c - 1] == '.' or addr[c - 1] == '"'):
            c = c + 1
            while c < len(addr):
                if addr[c] == '"': break
                if addr[c] == '\\' and addr[c + 1] == ' ':
                    c = c + 2
                    continue
                if ord(addr[c]) < 32 or ord(addr[c]) >= 127: return 0
                c = c + 1
            else: return 0
            if addr[c] == '@': break
            if addr[c] != '.': return 0
            c = c + 1
            continue
        if addr[c] == '@': break
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127: return 0
        if addr[c] in _rfc822_specials: return 0
        c = c + 1
    if not c or addr[c - 1] == '.': return 0

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    if domain >= len(addr): return 0
    count = 0
    while c < len(addr):
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.': return 0
            count = count + 1
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127: return 0
        if addr[c] in _rfc822_specials: return 0
        c = c + 1

    return count >= 1



class EmailField(BaseField):
    def __init__(self, label = u"Email", *args, **kwargs):
        super(EmailField, self).__init__(label, *args, **kwargs)
    def specValidate(self, value):
        if _isAddressValid(value) == 0:
            return ERROR_MSGS["invalidMail"]
        return None


class LinkField(BaseField):
    def __init__(self, label, toModelTransform = insertHttpPrefix, *arg, **kwargs):
        super(LinkField, self).__init__(label = label, toModelTransform = toModelTransform, * arg, **kwargs)

    def specValidate(self, value):
#        TODO
        return None

def putBrPhoneSigns(phone):
    if not phone:
        return u""
    return u"(" + phone[0:2] + u") " + phone[2:6] + u"-" + phone[6:10]

def removeBrPhoneSings(phone):
    if (not phone) or phone == u"":
        return None
    return phone[1:3] + phone[5:9] + phone[10:14]


class BrPhoneField(BaseField):
    def __init__(self, label = u"Telefone", toModelTransform = removeBrPhoneSings, fromModelTransform = putBrPhoneSigns, *arg, **kwargs):
        super(BrPhoneField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)

    def specValidate(self, value):
        if len(value) == 14:
            value = self.toModelTransform(value)
            try:
                int(value)
                return None
            except Exception:
                pass
        return ERROR_MSGS["invalidBrPhone"]
    
def putCepSign(cep):
    if not cep:
        return u""
    return cep[0:5] + u"-" + cep[5:9]

def removeCepSing(cep):
    if (not cep) or cep == u"":
        return None
    return cep[0:5] + cep[6:9]


class CepField(BaseField):
    def __init__(self, label = u"CEP", toModelTransform = removeCepSing, fromModelTransform = putCepSign, *arg, **kwargs):
        super(CepField, self).__init__(label = label, toModelTransform = toModelTransform, fromModelTransform = fromModelTransform, * arg, **kwargs)

    def specValidate(self, value):
        if len(value) == 9:
            value = self.toModelTransform(value)
            try:
                int(value)
                return None
            except Exception:
                pass
        return ERROR_MSGS["invalidCep"]


class BrState(BaseField):
    def __init__(self, label = u"Estado", *arg, **kwargs):
        super(BrState, self).__init__(label = label, * arg, **kwargs)

    def specValidate(self, value):
        return None


class BrTown(BaseField):
    def __init__(self, label = u"Cidade", *arg, **kwargs):
        super(BrTown, self).__init__(label = label, * arg, **kwargs)

    def specValidate(self, value):
        return None


class FieldsDescriptor(object):
    _propToField = {str(db.EmailProperty):EmailField, str(db.StringProperty):RequiredField, 
                    str(db.LinkProperty):LinkField,str(db.BooleanProperty):BooleanField,
                    str(db.IntegerProperty):IntField,str(db.StringListProperty):MultipleStringField}
    
    def __init__(self, modelClass=None,validator=None):
        d = {}
        f = self.fields()
        names = []
        for dic in f:
            k = dic.keys()[0]
            names.append(k)
            v = dic[k]
            if isinstance(v, BaseField):
                d[k] = v
            elif isinstance(v, basestring):
                d[k] = self.toField(modelClass, k, v)
        self.validator=validator
        self.fieldsDict = d
        self.fieldNames = names

    def fields(self):
        raise NotImplementedError("Must be implemented by subclasses")

    def validate(self, **kwargs):
        errors = {}
        if self.validator:
            dic=self.validator(kwargs)
            for k in dic:
                errors[k]=dic[k]
        for k in self.fieldsDict:
            v = self.fieldsDict[k]
            msg = v.validate(kwargs[k])
            if msg:
                errors[k] = msg
        
        return errors

    def toField(self, modelClass, prop, label):
        p = getattr(modelClass, prop)
        return FieldsDescriptor._propToField[str(p.__class__)](required = p.required, label = label)

    def buildModelPropertiesDict(self, **kwargs):
        modelDict = {}
        for k in self.fieldsDict:
            v = self.fieldsDict[k]
            modelDict[k] = v.transformToModel(kwargs[k])
        return modelDict

    def buildFieldValuesDict(self, modelInstance):
        fieldDict = {}
        for k in self.fieldsDict:
            v = self.fieldsDict[k]
            fieldDict[k] = v.transformFromModel(getattr(modelInstance, k))
        return fieldDict

    def setModelPropertiesDict(self, modelInstance, **kwargs):
        for k in self.fieldsDict:
            v = self.fieldsDict[k]
            setattr(modelInstance, k, v.transformToModel(kwargs[k]))
