from datetime import datetime
from flask import current_app as app
from bson import ObjectId
from eve.methods import (
    get as web_get,
    post as _web_post,
    delete as _web_delete,
    patch as _web_patch,
    common
    )
from eve.utils import config


def str2id(value):
    if isinstance(value, ObjectId):
        pass
    elif isinstance(value, str):
        return ObjectId(value)
    elif isinstance(value, list):
        return list(map(str2id, value))
    elif isinstance(value, dict) and '_id' in value:
        value['_id'] = str2id(value['_id'])
    return value

def id2str(value):
    if isinstance(value, str):
        pass
    elif isinstance(value, ObjectId):
        return str(value)
    elif isinstance(value, list):
        return list(map(id2str, value))
    elif isinstance(value, dict) and '_id' in value:
        value['id'] = id2str(value['_id'])
    return value

def _get_validator(resource):
    resource_def = app.config["DOMAIN"][resource]
    schema = resource_def["schema"]
    allow_unknown = resource_def["allow_unknown"]
    validator = app.validator(schema, resource=resource, allow_unknown=allow_unknown)
    return validator

def _set_document_time(document, time=None, create=False):
    if time is None:
        time = datetime.utcnow().replace(microsecond=0)

    if create:
        document.setdefault(config.DATE_CREATED, time)
    document[config.LAST_UPDATED] = time
    return document

def _set_soft_delete(resource, document):
    if config.DOMAIN[resource]["soft_delete"] is True:
        document[config.DELETED] = False

def _trans_input(resource, lookup=None, payload=None):
    if payload:
        if all([key.startswith('$') for key in payload.keys()]):
            for key, value in payload.items():
                payload[key] = common.parse(payload[key], resource)
            payload['$set'] = _set_document_time(payload.get('$set', {}))
        else:
            payload = common.parse(payload, resource)
    if lookup:
        lookup = common.parse(lookup, resource)
        _set_soft_delete(resource, lookup)
    return lookup, payload

def _parse_documents(resource, documents, validator=None):
    if validator is None:
        validator = _get_validator(resource)

    if isinstance(documents, dict):
        documents = [documents]

    for num, document in enumerate(documents):
        documents[num] = _parse_document(resource, document, validator)

    return documents

def _parse_document(resource, document, validator=None):
    if validator is None:
        validator = _get_validator(resource)

    document = common.parse(document, resource)
    validation = validator.validate(document)
    document = validator.document

    _set_document_time(document, create=True)
    _set_soft_delete(resource, document)

    common.resolve_user_restricted_access(document, resource)
    common.store_media_files(document, resource)
    common.resolve_document_version(document, resource, "POST")
    return document

def get(resource, lookup):
    lookup, _ = _trans_input(resource, lookup=lookup)
    result = app.data.driver.db[resource].find_one(lookup)
    return id2str(result) if result else result

def get_many(resource, lookup):
    lookup, _ = _trans_input(resource, lookup=lookup)
    result = app.data.driver.db[resource].find(lookup)
    return result

def delete(resource, lookup):
    lookup, _ = _trans_input(resource, lookup=lookup)
    if config.DOMAIN[resource]["soft_delete"] is True:
        patch(resource, {'$set': {config.DELETED: True}}, lookup)
    else:
        app.data.driver.db[resource].delete_one(lookup)

def delete_many(resource, lookup):
    if config.DOMAIN[resource]["soft_delete"] is True:
        patch_many(resource, {'$set': {config.DELETED: True}}, lookup)
    else:
        app.data.driver.db[resource].delete_many(lookup)

def patch(resource, payload, lookup):
    lookup, document = _trans_input(resource, lookup=lookup, payload=payload)
    app.data.driver.db[resource].update_one(lookup, document)

def patch_many(resource, payload, lookup):
    lookup, document = _trans_input(resource, lookup=lookup, payload=payload)
    app.data.driver.db[resource].update_many(lookup, document)

def post(resource, payload):
    document = _parse_document(resource, payload)
    result = app.data.driver.db[resource].insert_one(document)
    return id2str({'_id': result.inserted_id})

def post_many(resource, payload):
    documents = _parse_documents(resource, payload)
    result = app.data.driver.db[resource].insert_many(documents)
    return [
        id2str({'_id': id_})
        for id_ in result.inserted_ids
    ]

def web_post(resource, payload):
    response, _, _, code, _ = _web_post(resource, payl=payload)
    if code == 201:
        id2str(response)
        code = 200
    return response, code

def web_delete(resource, lookup):
    _web_delete(resource, **lookup)

def web_patch(resource, payload, lookup):
    response, _, _, code = _web_patch(resource, payload=payload, **lookup)
    if code == 200:
        id2str(response)
    return response, code
