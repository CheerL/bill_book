from eve.auth import TokenAuth
from page.encrypt import jwt_run
from flask import request, current_app as app
from data_base import operator


class BaseAuth(TokenAuth):
    def get_resource_instance(self, resource, resource_id):
        return operator.get(resource, {'_id': resource_id})

    def instance_auth(self, resource_instance, user_id, method):
        raise NotImplementedError

    def resource_auth(self, resource, user_id, method):
        raise NotImplementedError

    def check_auth(self, token, allowed_roles, resource, method):
        status, msg, jwt, payload = jwt_run(jwt=token)
        if not status:
            return False

        user_id = payload['user']
        args = request.view_args
        if args:
            resource_instance = self.get_resource_instance(resource, args['_id'])
            return self.instance_auth(resource_instance, user_id, method)
        else:
            return self.resource_auth(resource, user_id, method)
