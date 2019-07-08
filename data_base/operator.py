from flask import current_app as app
from bson import ObjectId
from eve.methods import (
    get as web_get,
    post as _web_post,
    delete as _web_delete,
    patch as web_patch
    )


def str2id(value):
    if isinstance(value, str):
        return ObjectId(value)
    elif isinstance(value, list):
        return list(map(str2id, value))
    elif isinstance(value, dict) and '_id' in value:
        value['_id'] = ObjectId(value['_id'])

    return value


def id2str(value):
    if isinstance(value, ObjectId):
        return str(value)
    elif isinstance(value, list):
        return list(map(id2str, value))
    elif isinstance(value, dict) and '_id' in value:
        value['_id'] = str(value['_id'])

    return value

def get(resource, lookup):
    resource = app.data.find_one_raw(resource, **str2id(lookup))
    if resource:
        return id2str(resource)
    return None

def delete(resource, lookup):
    app.data.remove(resource, str2id(lookup))

def web_post(resource, payload):
    response, _, _, return_code, _ = _web_post(resource, payl=payload)
    if return_code == 201:
        id2str(response)
    return response, return_code

def web_delete(resource, lookup):
    return _web_delete(resource, **str2id(lookup))
