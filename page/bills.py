from auth import BaseAuth
from data_base import operator
from page.billbook_user_relation import check_billbook_lookup, get_user_billbook_relation, get_transfer_billbook
from page.accounts import change_account_amount
from page.common import del_immutable_field, set_data, get_data, abort


class BillAuth(BaseAuth):
    def instance_auth(self, bill, method):
        user = get_data('user')
        if not user:
            return False

        creater = bill.get('creater')
        relation = operator.get('billbook_user_relation', {
            'user': user['_id'],
            'billbook': bill['billbook']
        })
        billbook = operator.get('billbooks', {'_id': bill['billbook']})

        relation_status = relation['status'] if relation else 4
        billbook_status = billbook['status']
        # set_data('relation', relation)
        if method in ['PATCH', 'DELETE']:
            return billbook_status == 0 or relation_status <= 1 or (user['_id'] is creater and relation_status <= 2)
        elif method == 'GET':
            return billbook_status <= 1 or relation_status is not None
        return False

    def resource_auth(self, method):
        return True

def get_normal_account(trans_account):
    if trans_account and trans_account.startswith('transfer'):
        return trans_account[8:]
    return trans_account


def _check_bill_cats(bill):
    billbook = bill.get('billbook')
    text = bill.get('cat_0')
    label = bill.get('cat_1', '')
    cat = operator.get('bill_categorys', {'billbook': billbook, 'text': text})
    if cat and label:
        if cat.get('labels', []):
            operator.patch('bill_categorys', {
                           '$push': {'labels': label}}, {'_id': cat['_id']})
        else:
            operator.patch('bill_categorys', {
                           '$set': {'labels': [label]}}, {'_id': cat['_id']})


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
        relation = operator.get('billbook_user_relation', {
            'user': user['_id'],
            'billbook': bill['billbook']
        })

        if not relation:
            billbook = operator.get('billbooks', {'_id': bill['billbook']})
            if billbook['status'] > 0:
                abort(400)
        elif relation['status'] > 2:
            abort(400)

        bills[num]['creater'] = user['_id']
        bills[num]['creater_name'] = user['nickname']

        if get_transfer_billbook(user['_id']) != bill['billbook']:
            _check_bill_cats(bill)

def post_insert_bills(bills):
    '''
    After insert bill:
        1. Change the amont of the account of this bill
    '''
    user = get_data('user', 409)
    transfer = get_transfer_billbook(user['_id'])

    for bill in bills:
        amount = bill['amount']
        change_account_amount(bill['account'], amount)
        if transfer == bill['billbook']:
            payer_id = bill.get('payer')
            consumer_id = bill.get('consumer')
            payer = operator.str2id(get_normal_account(payer_id)) if payer_id else None
            consumer = operator.str2id(get_normal_account(consumer_id)) if consumer_id else None
            change_account_amount(payer if bill['account'] != payer else consumer, -amount)


# R
def pre_get_bills(req, lookup):
    if lookup.get('_id', None) is None:
        user = get_data('user', 409)
        relation = get_user_billbook_relation(user['_id'], True)
        billbook = lookup.get('billbook', None)

        if billbook:
            lookup['billbook'] = check_billbook_lookup(
                billbook, user['_id'], relation)
        else:
            lookup['billbook'] = {'$in': list(relation.keys())}

def post_get_bills(res):
    user = get_data('user', 409)
    if user:
        transfer_billbook = get_transfer_billbook(user['_id'])
        if '_items' in res:
            for index, bill in enumerate(res['_items']):
                if bill['billbook'] == transfer_billbook:
                    res['_items'][index]['billbook'] = 'transfer'
        else:
            if res['billbook'] == transfer_billbook:
                res['billbook'] = 'transfer'
    return res


# U
def pre_update_bills(updates, bill):
    del_immutable_field(updates, ['creater', 'billbook'])

def post_update_bills(updates, bill):
    ori_amount = bill['amount']
    ori_account = bill['account']
    amount = updates.get('amount', ori_amount)
    account = updates.get('account', ori_account)
    user = get_data('user', 409)
    transfer_billbook = get_transfer_billbook(user['_id'])

    if bill['billbook'] != transfer_billbook:
        if account != ori_account:
            change_account_amount(ori_account, -ori_amount)
            change_account_amount(account, amount)
        elif amount != ori_amount:
            change_account_amount(ori_account, amount - ori_amount)
        _check_bill_cats(bill)
    else:
        ori_payer = bill['payer']
        ori_consumer = bill['consumer']
        payer_id = updates.get('payer', ori_payer)
        consumer_id = updates.get('consumer', ori_consumer)
        payer = operator.str2id(get_normal_account(payer_id)) if payer_id else None
        consumer = operator.str2id(get_normal_account(consumer_id)) if consumer_id else None

        if amount != ori_amount:
            change_account_amount(account, amount - ori_amount)
            change_account_amount(payer if account != payer else consumer, ori_amount - amount)


# D
def post_delete_bills(bill):
    user = get_data('user', 409)
    transfer = get_transfer_billbook(user['_id'])
    amount = bill['amount']

    change_account_amount(bill['account'], -amount)
    if transfer == bill['billbook'] and bill['payer'] and bill['consumer']:
        payer_id = bill.get('payer')
        consumer_id = bill.get('consumer')
        payer = operator.str2id(get_normal_account(payer_id)) if payer_id else None
        consumer = operator.str2id(get_normal_account(consumer_id)) if consumer_id else None
        change_account_amount(payer if bill['account'] != payer else consumer, amount)
