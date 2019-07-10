from data_base import operator
from auth import BaseAuth
from flask import abort

FULL_CAT_SPLITER = '#!~@^!#'

class CategoryAuth(BaseAuth):
    def instance_auth(self, resource_instance, user, method):
        bill_book = operator.get('bill_books', {'_id': resource_instance['bill_book']})
        owners = bill_book.get('owners', [])
        managers = bill_book.get('managers', [])
        writers = bill_book.get('writers', [])
        readers = bill_book.get('readers', [])

        if method in ['DELETE', 'PATCH']:
            return user['_id'] in owners
        elif method == 'GET':
            return user['_id'] in owners + writers + readers
        return False

    def resource_auth(self, resource, user, method):
        return True

def _get_bill_lookup(full_cat, bill_book, *args, **kwargs):
    lookup = {
        'bill_book': bill_book
    }
    for level, cat_name in enumerate(full_cat.split(FULL_CAT_SPLITER)):
        lookup['cat_%d' % level] = cat_name
    return lookup

def _get_cat_lookup(name, level, bill_book, parent=None, *args, **kwargs):
    lookup = {
        'bill_book': bill_book,
        'name': name,
        'level': level,
        'parent': parent
    }
    if parent:
        parent = operator.get('bill_categorys', {'_id': parent})

    if level is 0:
        lookup['full_cat'] = name
        del lookup['parent']
    elif level in [1, 2] and parent and parent['level'] in [0, 1]:
        lookup['full_cat'] = FULL_CAT_SPLITER.join([parent['full_cat'], name])
        lookup['bill_book'] = parent['bill_book']
        lookup['level'] = parent['level'] + 1
    else:
        return {}
    return lookup

def check_cat(name, level, bill_book, parent=None, *args, **kwargs):
    lookup = _get_cat_lookup(name, level, bill_book, parent)
    cat = operator.get('bill_categorys', lookup)
    return cat

def create_cat(name, level, bill_book, parent=None, *args, **kwargs):
    lookup = _get_cat_lookup(name, level, bill_book, parent)
    cat = operator.get('bill_categorys', lookup)
    if not cat:
        cat_id = operator.post('bill_categorys', lookup)
        cat = operator.get('bill_categorys', {'_id': cat_id['_id']})
    return cat

def delete_cat(cat, bill=True):
    operator.delete_many('bill_categorys', {
        'bill_book': cat['bill_book'],
        'full_cat': {
            '$regex': r'^%s' % cat['full_cat']
        }
    })

    if bill:
        bill_lookup = _get_bill_lookup(**cat)
        operator.delete_many('bills', bill_lookup)

def pre_insert_bill_categorys(cats):
    for num, cat in enumerate(cats):
        lookup = _get_cat_lookup(**cat)
        if not lookup or operator.get('bill_categorys', lookup):
            abort(400)
        else:
            cats[num] = lookup

def pre_update_bill_categorys(payload, cat):
    for readonly_field in ['parent', 'full_cat', 'level', 'bill_book']:
        if readonly_field in payload:
            del payload[readonly_field]

    if 'name' in payload:
        name = payload['name']
        level = cat['level']
        bill_book = cat['bill_book']
        ori_full_cat = cat['full_cat']
        full_cat_list = ori_full_cat.split(FULL_CAT_SPLITER)
        full_cat_list[-1] = name
        full_cat = FULL_CAT_SPLITER.join(full_cat_list)

        if operator.get('bill_categorys', {'full_cat': full_cat, 'bill_book': bill_book}):
            del payload['name']
            abort(400)

        payload['full_cat'] = full_cat
        for tmp_cat in operator.get_many('bill_categorys', {
            'bill_book': bill_book,
            'full_cat': {
                '$regex': r'^%s' % ori_full_cat
            }}):
            if tmp_cat['_id'] == cat['_id']:
                continue
            tmp_full_cat = tmp_cat['full_cat'].replace(ori_full_cat, full_cat, 1)
            operator.patch('bill_categorys', {'$set': {'full_cat': tmp_full_cat}}, {'_id': tmp_cat['_id']})

        bill_lookup = _get_bill_lookup(**cat)
        operator.patch_many('bills', {'$set': {'cat_%d' % level: name}}, bill_lookup)

def post_delete_bill_categorys(cat):
    delete_cat(cat)
