bills = {
    'item_title': 'bill',
    'schema': {
        'bill_book': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'bill_books',
                'embeddable': True
            }
        },
        'time': {
            'type': 'datetime',
            'required': True
        },
        'account': {
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
                'embeddable': True
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
                'resource': 'userinfos',
                'embeddable': True
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