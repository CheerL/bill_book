from page.bill_categorys import CategoryAuth

bill_categorys = {
    'item_title': 'bill_category',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'authentication': CategoryAuth,
    'schema': {
        'name': {
            'type': 'string',
            'required': True
        },
        'level': {
            'type': 'integer',
            'required': True,
        },
        'bill_book': {
            'required': True,
            'type': 'objectid',
            'data_relation': {
                'resource': 'bill_books',
                'embeddable': False
            }
        },
        'full_cat': {
            'type': 'string'
            # 'readonly': True
        },
        'parent': {
            # 'required': True,
            # 'readonly': True,
            'dependencies': {'level': [1, 2]},
            'type': 'objectid',
            'data_relation': {
                'resource': 'bill_categorys',
                'embeddable': False
            }
        }
    }
}