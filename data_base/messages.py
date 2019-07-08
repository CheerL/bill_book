messages = {
    'item_title': 'message',
    'schema': {
        'from': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': True
            }
        },
        'to': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': True
            }
        },
        'time': {
            'type': 'datetime',
            'required': True,
        },
        'mtype': {
            'type': 'string'
        },
        'readed': {
            'type': 'boolen',
            'default': False
        },
        'content': {
            'type': 'string'
        },
    }
}