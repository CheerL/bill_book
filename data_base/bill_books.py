from auth import BaseAuth
from data_base import operator


class BillBookAuth(BaseAuth):
    def instance_auth(self, resource_instance, user_id, method):
        owners = resource_instance.get('owners', [])
        managers = resource_instance.get('managers', [])
        writers = resource_instance.get('writers', [])
        readers = resource_instance.get('readers', [])
        user = operator.str2id(user_id)

        if method == 'DELETE':
            return user in owners
        elif method == 'PATCH':
            return user in owners + writers
        elif method == 'GET':
            return user in owners + writers + readers
        return False

    def resource_auth(self, resource, user_id, method):
        return True


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
            # 'default': ''
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
                    'embeddable': True
                }
            },
        },
        'managers': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': True
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
                    'embeddable': True
                },
                'nullable': True
            },
            'default': []
        },
        'readers': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'user_infos',
                    'embeddable': True
                },
            },
            'default': []
        },
        'cover': {
            'type': 'string',
            'default': 'cover'
        },
        'categorys': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'bill_categorys',
                    'embeddable': True
                },
            },
            'default': []
        },
        'recent_bills': {
            'type': 'list',
            'schema': {
                'type': 'objectid',
                'data_relation': {
                    'resource': 'bills',
                    'embeddable': True
                },
            },
            'default': []
        }
    }
}