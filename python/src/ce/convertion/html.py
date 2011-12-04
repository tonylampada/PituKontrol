# -*- coding: utf-8 -*-
'''
Created on 19/03/2011

@author: Renzo Nuccitelli
'''
from ce.convertion.field import EmailField, LinkField, BrPhoneField, BrState, \
    BrTown, CepField, BooleanField, RealCurrencyField, IntField,\
    RadioStringField, MultipleStringField
from google.appengine.ext import db


class TableColumn(object):
    def __init__(self, prop, label):
        self.label = label
        self.prop = prop


def _brStateHtml(prop, dataValue, field):
    item = '<select id="combostate" name="state" onchange="setTowns()" >\n'
    if dataValue:
        item = item + '<option value="' + dataValue + '" selected="yes"></option>\n'
    return item + '</select>\n'

def _brTownHtml(prop, dataValue, field):
    item = '<select id="combotown" name="town"  >\n'
    if dataValue:
        item = item + '<option value="' + dataValue + '" selected="yes"></option>\n'
    return item + '</select>\n'

def _brBooleanHtml(prop, dataValue, field):
    checkYes=(dataValue =="True") and 'checked="checked"' or ""
    str='<input type="radio" name="%s" value="True" %s />Sim'% (prop,checkYes)
    checkNo=(dataValue == "False") and 'checked="checked"' or ""
    return str+'<input type="radio" name="%s" value="False" %s />N&atilde;o'% (prop,checkNo)

def _radioHtml(prop, dataValue, field):
    labels=field.optLabels
    choices=field.choices
    str=""
    lblIndex=0;
    for c in choices:
        lbl=c
        if labels:
            lbl=len(labels)>lblIndex and labels[lblIndex] or c
        checked=(dataValue ==c) and "checked" or ""
        str=str+'<input type="radio" name="%s" value="%s" %s />%s<br>'%(prop,c,checked,lbl)
        lblIndex+=1
    return str

def _checkboxHtml(prop, dataValue, field):
    dataValue=dataValue or []
    labels=field.optLabels
    lblIndex=0;
    choices=field.choices
    str=""
    for c in choices:
        lbl=len(labels)>lblIndex and labels[lblIndex] or ""
        lblIndex+=1
        checked=(c in dataValue) and "checked" or ""
        str=str+'<input type="checkbox" name="%s" value="%s" %s />%s<br>' % (prop,c,checked,lbl)
    return str


class Builder(object):
    _fieldToHtmlFunction = {str(BrState):_brStateHtml, str(BrTown):_brTownHtml,str(BooleanField):_brBooleanHtml,
        str(RadioStringField):_radioHtml,str(MultipleStringField):_checkboxHtml}
    _defaultSizeDict = {str(EmailField):25, str(BrPhoneField):14,str(CepField):9}
    _filedToHtmlClassDict = {str(EmailField):"fieldEmail", str(LinkField):"fieldLink", str(BrPhoneField):"fieldBrPhone",
                             str(CepField):"fieldCep",str(RealCurrencyField):"fieldReal",str(IntField):"fieldInt"}

    def __init__(self, fieldsDescritor=None):
        self.fieldsDescritor = fieldsDescritor

    def buildRequestDict(self, request):
        d = {}
        for k in self.fieldsDescritor.fieldNames:
            if isinstance(self.fieldsDescritor.fieldsDict[k],MultipleStringField):
                d[k]=request.get_all(k)
            else:
                d[k] = request.get(k)
        return d

    def buildModelDict(self, request):
        return self.fieldsDescritor.buildModelPropertiesDict(**self.buildRequestDict(request))

    def validate(self, request):
        return self.fieldsDescritor.validate(**self.buildRequestDict(request))

    def setModelFromRequest(self, model, request):
        self.fieldsDescritor.setModelPropertiesDict(model, **self.buildRequestDict(request))

    def buildTable(self, items, extraColumns = None,title=None):
        t = "<table>\n<tr>"
        if title:
            t='<div class="tableTitle">'+title+'</div>\n'+t
        if extraColumns:
            for column in extraColumns:
                t = t + "<th>" + column.label + "</th>"
        if self.fieldsDescritor:
            for p in self.fieldsDescritor.fieldNames:
                t = t + "<th>" + self.fieldsDescritor.fieldsDict[p].label + "</th>"
        t = t + "</tr>\n"
        cycle = "odd"
        for i in items:
            t = t + '<tr class="' + cycle + '">'
            if extraColumns:
                for column in extraColumns:
                    t = t + "<td>" + getattr(i, column.prop) + "</td>"
            if self.fieldsDescritor:
                modelProps = self.fieldsDescritor.buildFieldValuesDict(i)
                for p in self.fieldsDescritor.fieldNames:
                    someProp=modelProps[p]
                    if isinstance(someProp, basestring):
                        someProp=someProp=="True" and "Sim" or someProp
                        someProp=someProp=="False" and "N&atilde;o" or someProp
                        t = t + "<td>" + someProp + "</td>"
                    else:
                        t = t + "<td>" + str(someProp) + "</td>"
            cycle = cycle == "odd" and "even" or "odd"
            t = t + "</tr>\n"
        return t + "</table>\n"

    def getFullForm(self, postLink, formTitle = None, data = None, errorMsgs = None, otherInputs = None):
        f = "<div>Campos marcados com * s&atilde;o obrigat&oacute;rios</div>"
        if errorMsgs:
            numError = len(errorMsgs)
            if numError > 0 :
                f = f + '<div class="errorMsg">Existe(m) ' + str(numError) + " erro(s). Corrija os campos com mensagens em vermelho.</div>"
        f = f + '<form action="' + postLink + '" method="POST">\n'
        f = f + self.getHtmlInputs(formTitle, data, errorMsgs)
        if otherInputs:
            f = f + otherInputs
        f = f + '<div class="row">\n<span class="formInput"><input type="submit" name="Submit" value="Cadastrar"/></span>\n</div>\n'
        return f + '<div class="spacer">&nbsp;</div>\n</form>\n'

    def getHtmlInputs(self, formTitle = None, data = None, errorMsgs = None):
        allInputs = u""
        if formTitle:
            allInputs = allInputs + u'<div class="row">\n<span class="formTitle">' + formTitle + u'</span>\n</div>\n'
        if  isinstance(data, db.Model):
            data = self.fieldsDescritor.buildFieldValuesDict(data)
        for k in self.fieldsDescritor.fieldNames:
            field = self.fieldsDescritor.fieldsDict[k]
            msg = errorMsgs and errorMsgs.get(k)
            input = u""
            if msg:
                input = input + u'<div class="row">\n<span class="errorMsg">' + msg + u'</span></div>\n'
            input = input + u'<div class="row">\n'
            dataValue = data and data.get(k)
            inputType = None
            func = self.fieldToHtmlFunction(field)
            if func:
                inputType = func(k, dataValue, field)
            else:
                inputType = u'<input type="text" class="' + self.fieldToHtmlClass(field) + u'" name="' + k + u'" size="' + self.fieldSize(field) + u'" ' + (dataValue is None and u" " or (u'value="' + dataValue + u'"')) + u' />'
            input = input + u'<span class="label">' + (field.required and u"* " or u"") + field.label + u':</span>'
            input = input + u'<span class="formInput">' + inputType + u'</span>\n'
            input = input + u"</div>\n"
            allInputs = allInputs + input
        return allInputs

    def fieldToHtmlFunction(self, field):
        return Builder._fieldToHtmlFunction.get(str(field.__class__))

    def fieldSize(self, field):
        return str(Builder._defaultSizeDict.get(str(field.__class__), 20))

    def fieldToHtmlClass(self, field):
        return Builder._filedToHtmlClassDict.get(str(field.__class__), "none")


