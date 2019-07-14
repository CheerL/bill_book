# from page.bill_book_user_relation import BillBookUserRelationAuth

bill_book_user_relation = {
    'item_title': 'bill_book_user_relation',
    'resource_methods': ['GET', 'POST'],
    'item_methods': ['GET', 'PATCH', 'DELETE'],
    # 'authentication': BillBookUserRelationAuth,
    'schema': {
        'user': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'user_infos',
                'embeddable': False
            }
        },
        'bill_book': {
            'type': 'objectid',
            'required': True,
            'data_relation': {
                'resource': 'bill_books',
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