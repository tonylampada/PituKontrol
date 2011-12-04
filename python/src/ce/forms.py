# -*- coding: utf-8 -*-
'''
Created on 12/07/2011

@author: Renzo Nuccitelli
'''
from google.appengine.ext import db
from ce import validation, transformation

REQUIRED_FIELD_ERROR_MSG=u"Campo Obrigatório"
INVALID_OPTION_MSG=u"Opção Inválida"
INVALID_MAIL=u"Email Inválido"
INVALID_FIELD=u"Campo Inválido"
MULTILINE_MSG=u"Campo não aceita que se pule linha"
STRING_TOO_LONG=u"Tamanho máximo de 500 carateres"



def _handle_db_propert_attrs(property,validator):
    if property.required:
        return validation.composition(validation.required_string_validator,\
                validator)
    else:
        return validator

def boolean_validator_generator(property):
    return _handle_db_propert_attrs(property,validation.boolean_validator)
    
    
def int_validator_generator(property):
    return _handle_db_propert_attrs(property,validation.int_validator)

def float_validator_generator(property):
    return _handle_db_propert_attrs(property,validation.float_validator)

def linkValidatorGenerator(property):
    return _handle_db_propert_attrs(property,validation.link_validator)


DEFAULT_VALIDATORS={db.BooleanProperty:boolean_validator_generator,\
    db.IntegerProperty:int_validator_generator,db.FloatProperty:float_validator_generator,\
    db.LinkProperty:linkValidatorGenerator}

DEFAULT_TRANSFORMATIONS={db.BooleanProperty:transformation.string_to_boolean,\
    db.FloatProperty:transformation.string_to_float,db.IntegerProperty:transformation.string_to_int,\
    db.LinkProperty:transformation.string_to_link}

def _validate_generator(property):
    def validate(value):
        try:
            property.validate(value)
            return None
        except Exception,e:
            msg=str(e)
            if msg.find("is required")>=0:
                return REQUIRED_FIELD_ERROR_MSG
            elif msg.find("email must not be empty")>=0:
                return None
            elif msg.find("choice")>=0 or msg.find("a bool")>=0:
                return INVALID_OPTION_MSG
            elif msg.find("is not multi-line")>=0:
                return MULTILINE_MSG
            elif msg.find("Consider Text instead")>=0:
                return STRING_TOO_LONG
            return INVALID_FIELD
    return validate

def default_validator(property):
    return DEFAULT_VALIDATORS.get(property.__class__,_validate_generator)(property)

def transform(property):
    return DEFAULT_TRANSFORMATIONS.get(property.__class__,transformation.string_to_none)

formBase='''<div class="line"> 
    <div class="errorMsg" >{{errors.%s}}</div> 
    <div class="left">%s</div> 
    <div class="right"><input type="text" name="%s"  value="{{%s.%s|noneTo:''}}" /></div> 
    <div class="spacer"></div> 
</div>''' 

class Form():
    def __init__(self,modelClass,exclude=(),requestValidator=None,validators={},transformations={}):
        props=modelClass.properties()
        keys=[k for k in props.keys() if not k.startswith("_")]
        keys=set(keys)
        exclude=set(exclude)
        foundProps=keys.difference(exclude)
        self.transformations={}
        def f(result,key):
            result[key]=default_validator(props[key])
            self.transformations[key]=transform(props[key])
            return result
        self.validators=reduce(f,foundProps,{})
        self.validators.update(validators)
        self.transformations.update(transformations)
        self.requestValidator=requestValidator
        
    def validate(self,request):
        def f(errors,key):
            er=self.validators[key](request.get(key))
            if er is not None:
                errors[key]=er
            return errors
        allErrors=reduce(f,self.validators.keys(),{})
        if self.requestValidator:
            allErrors.update(self.requestValidator(request))
        return allErrors
    
    def transform(self,request):
        def f(dic,key):
            val=self.transformations[key](request.get(key))
            dic[key]=val
            return dic
        dictionary=reduce(f,self.transformations.keys(),{})
        return dictionary
    
    def fill(self,request,modelInstace):
        def f(m,key):
            val=self.transformations[key](request.get(key))
            setattr(m, key, val) 
            return m
        model=reduce(f,self.transformations.keys(),modelInstace)
        return model
    
    def generate_html_form(self,prefix=""):
        form=""
        for p in self.validators.keys():
            form+=formBase%(p,p,p,prefix,p)
        return form 
