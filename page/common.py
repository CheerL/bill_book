from flask import g, abort

def del_immutable_field(updates, fields):
    for field in fields:
        if field in updates:
            del updates[field]

def del_unchanged_field(updates, original):
    for key, value in updates.items():
        if value == original[key]:
            del updates[key]

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
