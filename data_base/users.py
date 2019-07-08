users = {
    'item_title': 'user',

    # 'additional_lookup': {
    #     'url': 'regex("[\w]+")',
    #     'field': 'lastname'
    # },
    'internal_resource': True,
    'schema': {
        'account': {
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
        }
    }
}