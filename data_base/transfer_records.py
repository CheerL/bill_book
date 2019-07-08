transfer_records = {
    'item_title': 'transfer_record',
    'schema': {
        'from': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'accounts',
                'embeddable': True
            }
        },
        'to': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'accounts',
                'embeddable': True
            }
        },
        'time': {
            'type': 'datetime',
            'required': True,
        },
        'amount': {
            'type': 'float',
            'required': True,
        },
        'remark': {
            'type': 'string'
        }
    }
}