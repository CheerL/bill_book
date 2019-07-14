from auth import BaseAuth
from data_base import operator
from page.bill_book_user_relation import check_bill_book_lookup, get_user_bill_book_relation
from page.bill_categorys import get_or_create_cat
from page.accounts import change_account_amount
from page.common import del_immutable_field, set_data, get_data, abort

class BillAuth(BaseAuth):
    def instance_auth(self, bill, method):
        user = get_data('user')
        if not user:
            return False

        creater = bill.get('creater')
        relation = operator.get('bill_book_user_relation', {
            'user': user['_id'],
            'bill_book': bill['bill_book']
        })
        bill_book = operator.get('bill_books', {'_id': bill['bill_book']})

        relation_status = relation['status'] if relation else None
        bill_book_status = bill_book['status']
        # set_data('relation', relation)

        if method in ['PATCH', 'DELETE']:
            return bill_book_status <= 0 or relation_status <=1 or (user['_id'] is creater and relation_status <= 2)
        elif method == 'GET':
            return bill_book_status <= 1 or relation_status is not None
        return False

    def resource_auth(self, method):
        return True

def _check_bill_cats(bill):
    bill_book = bill['bill_book']

    parent = None
    for level in range(3):
        cat_name = bill.get('cat_%d' % level, '')
        if not cat_name:
            break

        cat = get_or_create_cat(cat_name, level, bill_book, parent)
        parent = cat['_id']

# C
def pre_insert_bills(bills):
    '''
    Before insert bill:
        1. Make sure now user is at least writer of the bill book of this bill.
        2. Set now user as the creater of this bill.
        3. Check related categorys, create if not existing.
    '''
    user = get_data('user', 409)

    for num, bill in enumerate(bills):
        relation = operator.get('bill_book_user_relation', {
            'user': user['_id'],
            'bill_book': bill['bill_book']
        })
        if relation['status'] > 3:
            abort(400)

        bills[num]['creater'] = user['_id']
        _check_bill_cats(bill)

def post_insert_bills(bills):
    '''
    After insert bill:
        1. Change the amont of the account of this bill
    '''
    for bill in bills:
        change_account_amount(bill['amount'], bill['account'])

# R
def pre_get_bills(req, lookup):
    user = get_data('user', 409)
    relation = get_user_bill_book_relation(user['_id'])
    bill_book = lookup.get('bill_book', None) 

    if bill_book:
        lookup['bill_book'] = check_bill_book_lookup(bill_book, user['_id'], relation)
    else:
        lookup['bill_book'] = {'$in': list(relation.keys())}

# U
def pre_update_bills(updates, bill):
    del_immutable_field(updates, ['creater', 'bill_book'])

def post_update_bills(updates, bill):
    ori_amount = bill['amount']
    ori_account = bill['account']
    amount = updates.get('amount', ori_amount)
    account = updates.get('account', None)

    if account:
        change_account_amount(-ori_amount, ori_account)
        change_account_amount(amount, account)
    elif amount != ori_amount:
        change_account_amount(amount - ori_amount, ori_account)

    _check_bill_cats(bill)

# D
def post_delete_bills(bill):
    change_account_amount(-bill['amount'], bill['account'])
