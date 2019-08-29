from flask import g, abort, current_app as app
from eve.utils import parse_request

def del_immutable_field(updates, fields):
    for field in fields:
        if field in updates:
            del updates[field]

def del_unchanged_field(updates, original):
    deleted_fields = []
    for field, value in updates.items():
        if field in original and value == original[field]:
            deleted_fields.append(field)

    for field in deleted_fields:
        del updates[field]

def get_data(key, error=None):
    tmp_data = g.get('tmp_data', {})
    data = tmp_data.get(key, None)
    
    if not data and error is not None:
        return abort(error)
    return data

def set_data(key, value):
    g.setdefault('tmp_data', {})
    g.tmp_data[key] = value

def pre_update(resource, updates, original):
    return del_unchanged_field(updates, original)

def pre_get(resource, req, lookup):
    parsed_req = parse_request(resource)
    parsed_req = app.data._convert_where_request_to_dict(parsed_req)
    lookup.update(parsed_req)
