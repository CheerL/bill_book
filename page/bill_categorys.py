from data_base import operator
from auth import BaseAuth
from page.common import abort, get_data
from page.bill_book_user_relation import get_user_bill_book_relation, check_bill_book_lookup

FULL_CAT_SPLITER = '#!~@^!#'

class CategoryAuth(BaseAuth):
    def instance_auth(self, cat, method):
        user = get_data('user')
        if not user:
            return False

        relation = operator.get('bill_book_user_relation', {
            'user': user['_id'],
            'bill_book': cat['bill_book']
        })
        # bill_book = operator.get('bill_books', {'_id': cat['bill_book']})
        # managers = get_bill_book_users(bill_book, 1, True)
        # writers = managers + get_bill_book_users(bill_book, 2)
        # readers = writers + get_bill_book_users(bill_book, 3)

        if method in ['DELETE', 'PATCH']:
            return relation['status'] <= 1
        elif method == 'GET':
            return relation is not None
        return False

    def resource_auth(self, method):
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

def get_or_create_cat(name, level, bill_book, parent=None, *args, **kwargs):
    lookup = _get_cat_lookup(name, level, bill_book, parent)
    cat = operator.get('bill_categorys', lookup)
    if not cat:
        cat = operator.post('bill_categorys', lookup)
    return cat

# C
def pre_insert_bill_categorys(cats):
    '''
    Before insert category:
        1. If the same category exists, stop
    '''
    for num, cat in enumerate(cats):
        lookup = _get_cat_lookup(**cat)
        if not lookup or operator.get('bill_categorys', lookup):
            abort(400)
        else:
            cats[num] = lookup

# R
def pre_get_cats(req, lookup):
    '''
    Before get category:
        1. If not specified bill books, limit the range as
           user's bill book.
        2. Given one bill book, continue if user have view privileges,
           otherwise stop with error 409
        3. Given many bill book, check each and remove unaccessible ones.
    '''
    user = get_data('user', 409)
    bill_book = lookup.get('bill_book', None)
    relation = get_user_bill_book_relation(user['_id'])
    user_bill_books = list(relation.keys())

    if bill_book:
        lookup['bill_book'] = check_bill_book_lookup(bill_book, user['_id'], relation)
    else:
        lookup['bill_book'] = {'$in': user_bill_books}

# U
def pre_update_bill_categorys(payload, cat):
    '''
    Before update category:
        1. Remove immutable fields 'parent', 'full_cat', 'level',
           'bill_book'
        2. If name is going to be change, check whether the same
           category exsits. If not, change the all related bills
           and categorys.
    '''
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


# D
def post_delete_bill_categorys(cat):
    '''
    After delete category:
        1. Delete all sub categorys of this category.
        2. Delete all related bills.
    '''
    operator.delete_many('bill_categorys', {
        'bill_book': cat['bill_book'],
        'full_cat': {
            '$regex': r'^%s' % cat['full_cat']
        }
    })

    bill_lookup = _get_bill_lookup(**cat)
    operator.delete_many('bills', bill_lookup)
