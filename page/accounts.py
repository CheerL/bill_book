from auth import BaseAuth
from data_base import operator
from page.common import abort, get_data, del_immutable_field

class AccountAuth(BaseAuth):
    def instance_auth(self, account, method):
        user = get_data('user')
        if not user:
            return False

        return user['_id'] == account.get('user')

    def resource_auth(self, method):
        return True

def change_account_amount(account, amount):
    operator.patch('accounts', {'$inc': {'amount': amount}}, {'_id': account})

# C
def pre_insert_accounts(accounts):
    '''
    Before insert accounts, for each account:
        1. Set now user as account creater
        2. Set account's default status to False.
           It's not allowed to create new default account,
           If you do want to do so, please do it in 2 steps:
            (1) Create a new account.
            (2) Set it default.
    '''
    user = get_data('user', 409)
    for num, account in enumerate(accounts):
        accounts[num]['user'] = user['_id']
        if account.get('default', False):
            accounts[num]['default'] = False

# R
def pre_get_accounts(req, lookup):
    '''
    Before get account:
        1. Set the user as now user. Users can only
           view their own account.
    '''
    user = get_data('user', 409)
    lookup['user'] = user['_id']

# U
def pre_update_accounts(updates, account):
    '''
    Before update account:
        1. Remove immutable fileds 'user' and 'account'.
        2. Check account's default status to make sure there
           is only one default account:
            (1) If updating account is default account,
                Its default status is not allowed to change.
            (2) If not, change this account to default and
                change original default account to normal acccount
    '''
    del_immutable_field(updates, ['user', 'amount'])

    if 'default' in updates:
        default = updates['default']
        ori_default = account.get('default', False)

        if default and not ori_default:
            operator.patch('accounts', {'$set': {'default': False}}, {'default': True, 'user': account['user']})
        elif not default and ori_default:
            del updates['default']

# D
def pre_delete_accounts(account):
    '''
    Before delete account:
        1. Default account is not allowed to be deleted.
           If you do want to do so, please do it in two
           steps:
            (1) Set any other existing account or create
                a new account as default account.
            (2) Delete original default account.
    '''
    if account['default']:
        abort(400)

def post_delete_accounts(account):
    '''
    After delete account:
        1. Transfer all the money in this account to default
           account.
        2. Change all bills belonging to this account to
           default account.
        3. #TODO Change all transfer record related to this
           account to default account 
    '''
    default_account = operator.get({'default': True, 'user': account['user']})
    deleted_amount = operator.aggregate(
        {'$group': {'_id': None, 'amount': {'$sum': '$amount'}}},
        {'account': account['_id']}
    )
    deleted_amount = next(default_account)['amount']
    print(deleted_amount, account['amount'])
    change_account_amount(default_account['_id'], account['amount'])
    operator.patch_many('bills', {'$set': {'account': default_account['_id']}}, {'account': account['_id']})
