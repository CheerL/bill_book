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
        'description': {
            'type': 'string',
            'default': ''
        },
        'status': {
            'type': 'string',
            'allowed': [
                'free',
                'public',
                'private',
                'close'
            ],
            'default': 'public'
        },
        'owners': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': False
                }
            },
            'required': True,
            'default': []
        },
        'managers': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': False
                }
            },
            'default': []
        },
        'writers': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': False
                },
            },
            'default': []
        },
        'readers': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': False
                },
            },
            'default': []
        },
        'cover': {
            'type': 'string',
            'default': 'cover'
        }
        # 'recent_bills': {
        #     'type': 'list',
        #     'schema': {
        #         'type': 'objectid',
        #         'data_relation': {
        #             'resource': 'bills',
        #             'embeddable': True
        #         },
        #     },
        #     'default': []
        # }
    }
}