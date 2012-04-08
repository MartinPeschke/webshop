from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseForbidden
import types, sha
from django.db import models
from django.utils import simplejson
from django.core.serializers.json import DateTimeAwareJSONEncoder
from decimal import *
from django.conf import settings

def _guard_bo(f):
    '''
    Return json format data, 'GET' method is now allowed.
    '''
    def new_f(*args, **kwargs):
        request = args[0]

        if args[0].method != 'POST':
            return HttpResponseNotAllowed([args[0].method])

        print 'received POST entry point'     
        login = request.POST.get('login', False)
        password =  request.POST.get('password', False)
        
        if not(login and password):
            return HttpResponseForbidden('No Login Provided!')
        print 'received Login & Password'
        bop_key = sha.new(password)
        if (settings.BOP_PUBLIC != bop_key.hexdigest()):
            return HttpResponseForbidden('Incorrect Login!')
        print 'Received Correct BOP Authentication'
        return f(*args, **kwargs)
    return new_f


def json_encode(data):
    """
    The main issues with django's default json serializer is that properties that
    had been added to a object dynamically are being ignored (and it also has 
    problems with some models).
    """

    def _any(data):
        ret = None
        if type(data) is types.ListType:
            ret = _list(data)
        elif type(data) is types.DictType:
            ret = _dict(data)
        elif isinstance(data, Decimal):
            # json.dumps() cant handle Decimal
            ret = str(data)
        elif isinstance(data, models.query.QuerySet):
            # Actually its the same as a list ...
            ret = _list(data)
        elif isinstance(data, models.Model):
            ret = _model(data)
        else:
            ret = data
        return ret
    
    def _model(data):
        ret = {}
        # If we only have a model, we only want to encode the fields.
        for f in data._meta.fields:
            ret[f.attname] = _any(getattr(data, f.attname))
        # And additionally encode arbitrary properties that had been added.
        fields = dir(data.__class__) + ret.keys()
        add_ons = [k for k in dir(data) if k not in fields and k[0] != '_']
        for k in add_ons:
            ret[k] = _any(getattr(data, k))
        return ret
    
    def _list(data):
        ret = []
        for v in data:
            ret.append(_any(v))
        return ret
    
    def _dict(data):
        ret = {}
        for k,v in data.items():
            ret[k] = _any(v)
        return ret
    
    ret = _any(data)
    
    return simplejson.dumps(ret, cls=DateTimeAwareJSONEncoder)



def json(f):
    '''
    Return json format data, 'GET' method is now allowed.
    '''
    def new_f(*args, **kwargs):
        result = f(*args, **kwargs)
        return HttpResponse(json_encode(result), mimetype='application/json')
    return new_f


