from auth import BaseAuth
from data_base import operator
from flask import abort

class AccountAuth(BaseAuth):
    def instance_auth(self, resource_instance, user, method):
        owner = resource_instance.get('user')
        return user['_id'] == owner

    def resource_auth(self, resource, user, method):
        return True


def pre_insert_accounts(accounts):
    for num, account in enumerate(accounts):
        if account.get('default', False):
            accounts[num]['default'] = False

def pre_delete_accounts(account):
    if account['default']:
        abort(400)

def pre_update_accounts(payload, account):
    if 'default' in payload:
        after = payload['default']
        before = account.get('default', False)
        if after == before:
            pass
        elif after and not before:
            operator.patch('accounts', {'$set': {'default': False}}, {'default': True, 'user': account['user']})
        elif not after and before:
            payload['default'] = True

def post_delete_accounts(account):
    default_account = operator.get({'default': True, 'user': account['user']})
    operator.patch_many('bills', {'$set': {'account': default_account['_id']}}, {'account': account['_id']})

