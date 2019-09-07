import data_base
import os

HOST = '0.0.0.0'
PORT = 5000

OPTIMIZE_PAGINATION_FOR_SPEED = True
# HATEOAS = False
MONGO_URI = 'mongodb://mongo:27017/bill_book{}'.format('_dev' if os.environ.get('BILLBOOK_BACKEND_DEV', False) else '')
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']
# PUBLIC_METHODS = []
# PUBLIC_ITEM_METHODS = []
IF_MATCH = False
URL_PREFIX = 'api'
API_VERSION = 'v1'
# ALLOWED_FILTERS = [*]
PAGINATION_LIMIT = 50
PAGINATION_DEFAULT = 50
# DEBUG = True
X_DOMAINS = '*'
X_HEADERS = [
    'Authorization',
    'Content-Type',
    'Access-Control-Allow-Origin',
    'Access-Control-Allow-Credentials',
    'Access-Control-Allow-Methods',
    'Cache-Control'
    ]
X_ALLOW_CREDENTIALS = True

DOMAIN = {
    'accounts': data_base.accounts,
    'billbooks': data_base.billbooks,
    'billbook_user_relation': data_base.billbook_user_relation,
    'bill_categorys': data_base.bill_categorys,
    'bills': data_base.bills,
    'messages': data_base.messages,
    'transfer_records': data_base.transfer_records,
    'user_infos': data_base.user_infos,
    'users': data_base.users
}
