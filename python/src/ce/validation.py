# -*- coding: utf-8 -*-
'''
Created on 12/07/2011

@author: Renzo Nuccitelli
'''
from ce import transformation
from google.appengine.ext import db
REQUIRED_MSG="requiredField"
INVALID_BOOLEAN="invalidBoolean"
INVALID_INT="invalidInt"
INVALID_FLOAT="invalidInt"
INVALID_PHONE="invalidPhone"
INVALID_CEP="invalidCep"
INVALID_LINK="invalidLink"
BR_ERROR_MSGS = {"invalidMail":u"Email inválido", REQUIRED_MSG:u"Campo Obrigatório",
               INVALID_LINK:u"Link Inválido", INVALID_PHONE:u"Telefone Inválido. Exemplo válido: (12) 1212-1212",
               INVALID_CEP:u"CEP Inválido",INVALID_BOOLEAN:u"Opção Inválida","invalidvalueCurrency":u"Moeda Inválida",
               INVALID_INT:u"Valor Inválido",INVALID_FLOAT:u"Valor Inválido","invalidChoice":u"Opção Inválida","invalidChoices":u"Opções Inválidas"}

def composition(*validators):
    def f(currentValidator,nextValidator):
        def k(value):
            result=currentValidator(value)
            if result is not None:
                return result
            return nextValidator(value)
        return k
    return reduce(f,validators,lambda value: None)

def float_validator(value):
    if value is None or value=="":
        return None
    value=value.replace(".","")
    value=value.replace(",",".")
    try:
        float(value)
    except:
        return BR_ERROR_MSGS[INVALID_FLOAT]


def boolean_validator(value):
    if value is None or value=="":
        return None
    value=value.upper()
    if value!="TRUE" and value!="FALSE":
        return BR_ERROR_MSGS[INVALID_BOOLEAN]
    return None

def int_validator(value):
    if value is None or value=="":
        return None
    try:
        int(value)
    except:
        return BR_ERROR_MSGS[INVALID_INT]

def required_string_validator(value):
    if value=="" or value is None:
        return BR_ERROR_MSGS[REQUIRED_MSG]
    return None

def br_phone_validator(value):
    if value is None or value=="":
        return None
    value=transformation.remove_br_phone_signs(value)
    if len(value) == 10:
        try:
            int(value)
            return None
        except Exception:
            pass
    return BR_ERROR_MSGS[INVALID_PHONE]

def cep_validator(value):
    if value is None or value=="":
        return None
    value=transformation.cep(value)
    if len(value) == 8:
        try:
            int(value)
            return None
        except Exception:
            pass
    return BR_ERROR_MSGS[INVALID_CEP]

def link_validator(value):
    if value is None or value=="":
        return None
    link=transformation.string_to_link(value)
    try:
        db.LinkProperty().validate(link)
        return None
    except Exception:
            pass
    return BR_ERROR_MSGS[INVALID_LINK]