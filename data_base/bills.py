from page.bills import BillAuth

bills = {
    'item_title': 'bill',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'authentication': BillAuth,
    'schema': {
        'bill_book': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'bill_books',
                'embeddable': False
            }
        },
        'time': {
            'type': 'datetime',
            'required': True
        },
        'amount': {
            'type': 'float',
            'required': True
        },
        'remark': {
            'type': 'string',
            'default': ''
        },
        'account': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'accounts',
                'embeddable': False
            }
        },
        'consumer': {
            'type': 'string'
        },
        'payer': {
            'type': 'string'
        },
        'creater': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': False
            }
        },
        'cat_0': {
            'type': 'string',
            'required': True
        },
        'cat_1': {
            'type': 'string',
            # 'required': True,
            'dependencies': 'cat_0'
        },
        'cat_2': {
            'type': 'string',
            'dependencies': ['cat_0', 'cat_1'],
            # 'required': True
        }
    }
}