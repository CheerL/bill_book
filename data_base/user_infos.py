from page.user_infos import UserInfoAuth

user_infos = {
    'item_title': 'user_info',
    'resource_methods': ['GET'],
    'item_methods': ['GET', 'PATCH'],
    'authentication': UserInfoAuth,
    'schema': {
        'nickname': {
            'type': 'string',
            'required': True,
            'unique': True,
            'minlength': 2,
            'maxlength': 20,
        },
        'avatar': {
            'type': 'string',
            'default': 'default'
        }
    }
}