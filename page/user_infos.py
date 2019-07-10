from auth import BaseAuth

class UserInfoAuth(BaseAuth):
    def instance_auth(self, resource_instance, user, method):
        if method == 'PATCH':
            return user['_id'] == resource_instance['_id']
        elif method == 'GET':
            return True
        return False

    def resource_auth(self, resource, user, method):
        return True
