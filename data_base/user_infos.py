user_infos = {
    'item_title': 'user_info',
    'schema': {
        'nickname': {
            'type': 'string',
            'required': True,
            'unique': True,
            'minlength': 2,
            'maxlength': 20,
        },
        'user': {
            'type': 'objectid',
            'required': True,
            'unique': True,
            'data_relation': {
                'resource': 'users',
                'embeddable': False
            }
        },
        'avatar': {
            'type': 'string',
            'default': 'avatar'
        },
        'accounts': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'accounts',
                    'embeddable': True
                }
            }
        },
        'bill_books': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'bill_books',
                    'embeddable': True
                }
            }
        },
        'friends': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': True
                }
            }
        }
    }
}