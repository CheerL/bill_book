from page.bill_books import BillBookAuth

bill_books = {
    'item_title': 'bill_book',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'authentication': BillBookAuth,
    'schema': {
        'name': {
            'type': 'string',
            'required': True
        },
        'remark': {
            'type': 'string',
            'default': ''
        },
        'status': {
            # 0: free
            # 1: public
            # 2: private
            'type': 'integer',
            'min': 0,
            'max': 2,
            'default': 1
        },
        'default': {
            'type': 'boolean',
            'default': False
        },
        'cover': {
            'type': 'string',
            'default': 'default'
        }
    }
}