from data_base import operator
from auth import BaseAuth
from page.common import abort, get_data, del_immutable_field
from page.billbook_user_relation import get_user_billbook_relation, check_billbook_lookup

class CategoryAuth(BaseAuth):
    def instance_auth(self, cat, method):
        user = get_data('user')
        if not user:
            return False

        relation = operator.get('billbook_user_relation', {
            'user': user['_id'],
            'billbook': cat['billbook']
        })

        if method in ['DELETE', 'PATCH']:
            return relation['status'] <= 1
        elif method == 'GET':
            return relation is not None
        return False

    def resource_auth(self, method):
        return True

# C
def pre_insert_bill_categorys(cats):
    '''
    Before insert category:
        1. If the same category exists, stop
    '''
    for num, cat in enumerate(cats):
        billbook = cat.get('billbook')
        name = cat.get('name')
        if operator.get('bill_categorys', {'billbook': billbook, 'name': name}):
            abort(400)

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
    if lookup.get('_id', None) is None:
        user = get_data('user', 409)
        billbook = lookup.get('billbook', None)
        relation = get_user_billbook_relation(user['_id'])

        if billbook:
            lookup['billbook'] = check_billbook_lookup(billbook, user['_id'], relation)
        else:
            lookup['billbook'] = {'$in': list(relation.keys())}

# U
def pre_update_bill_categorys(updates, cat):
    '''
    Before update category:
        1. Remove immutable fields 'billbook'
        2. If name is going to be change, check whether the same
           category exsits. If not, change the all related bills
           and categorys.
    '''
    del_immutable_field(updates, ['billbook'])

    billbook = cat.get('billbook')
    name = updates.get('name', None)
    if name:
        if operator.get('bill_categorys', {'name': name, 'billbook': billbook}):
            abort(400)

        operator.patch_many('bills', {'$set': {'cat_0': name}}, {'billbook': billbook, 'cat_0': cat['name']})

# D
def post_delete_bill_categorys(cat):
    '''
    After delete category:
        2. Delete all related bills.
    '''
    operator.delete_many('bills', {'billbook': cat['billbook'], 'cat_0': cat['name']})
