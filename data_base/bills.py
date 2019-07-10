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
        'category': {
            'type': 'list',
            'required': True,
            'schema': {
                'type': 'dict',
                'schema': {
                    'name': {
                        'type': 'string',
                    },
                    'levle': {
                        'type': 'integer'
                    }
                }
            }
        }
    }
}