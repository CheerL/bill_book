from auth import BaseAuth
from data_base import operator
from page.common import abort, get_data, set_data, del_immutable_field
from page.billbook_user_relation import get_user_billbook_relation, check_billbook_lookup
from page.accounts import change_account_amount


class BillBookAuth(BaseAuth):
    def instance_auth(self, billbook, method):
        user = get_data('user')
        if not user:
            return False

        relation = operator.get(
            'billbook_user_relation',
            {'user': user['_id'], 'billbook': billbook['_id']}
        )
        if relation:
            set_data('relation', relation)
            relation_status = relation['status']
        else:
            relation_status = 4

        billbook_status = billbook['status']
        if method == 'DELETE':
            return relation_status <= 0
        elif method == 'PATCH':
            return relation_status <= 1
        elif method == 'GET':
            return billbook_status <= 1 or relation_status <= 3
        return False

    def resource_auth(self, method):
        return True

# C


def pre_insert_billbooks(billbooks):
    user = get_data('user', 409)
    relation = get_user_billbook_relation(user['_id'])

    for num, billbook in enumerate(billbooks):
        billbooks[num]['owners'] = [user['_id']]
        if num is 0 and not relation:
            billbooks[0]['default'] = True
        elif billbook.get('default', False):
            billbooks[num]['default'] = False


def post_insert_billbooks(billbooks):
    '''
    After insert billbooks, for each billbook:
        1. Set now user as owner
    '''
    user = get_data('user', 409)
    for billbook in billbooks:
        operator.post('billbook_user_relation', {
            'user': user['_id'],
            'billbook': billbook['_id'],
            'status': 0
        })

# R


def pre_get_billbooks(req, lookup):
    '''
    Before get billbooks, check lookup to make sure
    users can only view accessible bill books:
        1. If not specified bill books, limit the range as
           user's bill book.
        2. Given one bill book, continue if user have view privileges,
           otherwise stop with error 409
        3. Given many bill book, check each and remove unaccessible ones.
    '''
    if lookup.get('_id', None) is None:
        user = get_data('user', 409)
        relation = get_user_billbook_relation(user['_id'], lookup.get('name') == '***transfer***')
        # print
        billbook = lookup.get('_id', None)

        if billbook:
            lookup['_id'] = check_billbook_lookup(
                billbook, user['_id'], relation)
        else:
            lookup['_id'] = {'$in': list(relation.keys())}
        # print(lookup)

# U


def pre_update_billbooks(updates, billbook):
    '''
    Before update bill book:
        1. Only bill book's owners can change its status
    '''
    if 'status' in updates:
        relation = get_data('relation', 400)
        if relation['status'] > 0:
            del updates['status']

    if 'default' in updates:
        default = updates['default']
        ori_default = billbook.get('default', False)
        if default and not ori_default:
            user = get_data('user', 409)
            relation = get_user_billbook_relation(user['_id'])
            operator.patch_many(
                'billbooks',
                {'$set': {'default': False}},
                {'default': True, '_id': {'$in': list(relation.keys())}}
            )
        
        elif not default and ori_default:
            del updates['default']

# D
def pre_delete_billbooks(billbook):
    if billbook.get('default', False):
        abort(400)

def post_delete_billbooks(billbook):
    '''
    After delete bill book:
        1. Clear all relation between this book and users.
        2. Delete all bills belonging to this book.
    '''
    deleted = operator.aggregate('bills',
                                 {'$group': {'_id': '$account',
                                             'amount': {'$sum': '$amount'}}},
                                 {'billbook': billbook['_id']}
                                 )
    for each in deleted:
        change_account_amount(each['_id'], -each['amount'])

    operator.delete_many('billbook_user_relation', {
                         'billbook': billbook['_id']})
    operator.delete_many('bills', {'billbook': billbook['_id']})
