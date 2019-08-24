from eve.auth import TokenAuth
from page.encrypt import jwt_run
from page.common import set_data
from flask import request
from data_base import operator

class BaseAuth(TokenAuth):
    def get_resource_instance(self, resource, resource_id):
        return operator.get(resource, {'_id': resource_id})

    def instance_auth(self, resource_instance, method):
        raise NotImplementedError

    def resource_auth(self, method):
        raise NotImplementedError

    def check_auth(self, token, allowed_roles, resource, method):
        status, new, msg, jwt, payload = jwt_run(jwt=token)
        if not status:
            return False

        user_id = payload['user']
        user = operator.get('user_infos', {'_id': user_id})
        if not user:
            return False
        set_data('user', user)

        args = request.view_args
        if args:
            resource_instance = self.get_resource_instance(resource, args['_id'])
            return self.instance_auth(resource_instance, method)
        else:
            return self.resource_auth(method)
