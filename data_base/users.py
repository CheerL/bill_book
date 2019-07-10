users = {
    'item_title': 'user',
    # 'resource_methods': ['GET'],
    # 'item_methods': ['GET', 'PATCH'],
    'internal_resource': True,
    'schema': {
        'username' : {
            'type': 'string',
            'required': True,
            'unique': True,
            'minlength': 5,
            'maxlength': 30,
        },
        'password': {
            'type': 'string',
            'minlength': 5,
            'maxlength': 200,
            'required': True,
        },
        'info': {
            'type': 'objectid',
            'required': True,
            'unique': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': False
            }
        },
    }
}