from auth import BaseAuth
from data_base import operator

class BillAuth(BaseAuth):
    def instance_auth(self, resource_instance, user, method):
        bill_book = operator.get('bill_books', {'_id': resource_instance['bill_book']})
        owners = bill_book.get('owners', [])
        managers = bill_book.get('managers', [])
        writers = bill_book.get('writers', [])
        readers = bill_book.get('readers', [])
        creater = resource_instance.get('creater')

        if method == 'DELETE':
            return user['_id'] in owners + [creater]
        elif method == 'PATCH':
            return user['_id'] in owners + writers + [creater]
        elif method == 'GET':
            return user['_id'] in owners + writers + readers + [creater]
        return False

    def resource_auth(self, resource, user, method):
        return True
