bill_categorys = {
    'item_title': 'bill_category',
    'schema': {
        'name': {
            'type': 'string',
            'required': True
        },
        'level': {
            'type': 'integer',
            'required': True,
            'min': 1,
            'max': 3
        },
        'subcategorys': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'bill_categorys',
                    'embeddbable': True
                }
            }
        }
    }
}