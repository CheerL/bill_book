from page.billbook_user_relation import BillBookUserRelationAuth

billbook_user_relation = {
    'item_title': 'billbook_user_relation',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    'authentication': BillBookUserRelationAuth,
    'schema': {
        'user': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': True
            }
        },
        'billbook': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'billbooks',
                'embeddable': False
            }
        },
        'status': {
            # 0: owner
            # 1: manager
            # 2: writer
            # 3: reader
            'type': 'integer',
            'required': True,
            'min': 0,
            'max': 3
        }
    }
}