from page.accounts import AccountAuth

accounts = {
    'item_title': 'account',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'authentication': AccountAuth,
    'schema': {
        'name': {
            'type': 'string',
            'required': True,
            'default': 'default account'
        },
        'user': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': False
            }
        },
        'description': {
            'type': 'string',
            'default': ''
        },
        'icon': {
            'type': 'string',
            'default': 'icon'
        },
        'amount': {
            'type': 'float',
            'required': True,
            'default': 0.0
        },
        'default': {
            'type': 'boolean',
            'default': False
        }
    }
}