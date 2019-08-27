import data_base

HOST = '0.0.0.0'
PORT = 5000

OPTIMIZE_PAGINATION_FOR_SPEED = True
# HATEOAS = False
MONGO_URI = 'mongodb://home.pi:27017/bill_book'
RESOURCE_METHODS = ['GET', 'POST']
ITEM_METHODS = ['GET', 'PATCH', 'DELETE']
# PUBLIC_METHODS = []
# PUBLIC_ITEM_METHODS = []
CACHE_CONTROL = 'max-age=20'
CACHE_EXPIRES = 20
IF_MATCH = False
URL_PREFIX = 'api'
API_VERSION = 'v1'
# ALLOWED_FILTERS = [*]
PAGINATION_LIMIT = 50
# DEBUG = True
X_DOMAINS = '*'
X_HEADERS = ['Authorization', 'Content-Type', 'Access-Control-Allow-Origin', 'Access-Control-Allow-Credentials', 'Access-Control-Allow-Methods']
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
