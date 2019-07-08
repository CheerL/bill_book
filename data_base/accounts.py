accounts = {
    'item_title': 'account',
    'schema': {
        'name': {
            'type': 'string',
            'required': True,
            'default': '默认账户'
        },
        'description': {
            'type': 'string',
            'default': ''
        },
        'icon': {
            'type': 'string',
            'default': 'icon'
        },
        'balance': {
            'type': 'float',
            'required': True,
            'default': 0.0
        },
        'transfer_records': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'transfer_records',
                    'embeddable': True
                }
            }
        },
        'bills': {
            'type': 'set',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'bills',
                    'embeddable': True
                }
            }
        }
    }
}