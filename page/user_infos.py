from auth import BaseAuth
from page.common import get_data

class UserInfoAuth(BaseAuth):
    def instance_auth(self, infos, method):
        user = get_data('user')
        if not user:
            return False

        if method == 'PATCH':
            return user['_id'] == infos['_id']
        elif method == 'GET':
            return True
        return False

    def resource_auth(self, method):
        return True
