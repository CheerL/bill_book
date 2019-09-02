from page.bill_categorys import CategoryAuth

bill_categorys = {
    'item_title': 'bill_category',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'authentication': CategoryAuth,
    'schema': {
        'text': {
            'type': 'string',
            'required': True
        },
        'billbook': {
            'required': True,
            'type': 'objectid',
            'data_relation': {
                'resource': 'billbooks',
                'embeddable': False
            }
        },
        'icon': {
            'type': 'string',
            'required': True
        },
        'labels': {
            'type': 'list',
            'schema': {
                'type': 'string'
            },
            'default': []
        }
    }
}