from auth import BaseAuth
from data_base import operator

class BillBookAuth(BaseAuth):
    def instance_auth(self, resource_instance, user, method):
        owners = resource_instance.get('owners', [])
        managers = resource_instance.get('managers', [])
        writers = resource_instance.get('writers', [])
        readers = resource_instance.get('readers', [])

        if method == 'DELETE':
            return user['_id'] in owners
        elif method == 'PATCH':
            return user['_id'] in owners + writers
        elif method == 'GET':
            return user['_id'] in owners + writers + readers
        return False

    def resource_auth(self, resource, user, method):
        return True

def post_insert_bill_books(bill_books):
    for bill_book in bill_books:
        for owner in bill_book.get('owners', []):
            operator.patch('user_infos', {'$push': {'bill_books': bill_book['_id']}}, {'_id': owner})

def post_delete_bill_books(bill_book):
    for owner in bill_book.get('owners', []):
        operator.patch('user_infos', {'$pull': {'bill_books': bill_book['_id']}}, {'_id': owner})

    operator.delete_many('bills', {'bill_book': bill_book['_id']})
    operator.delete_many('bill_categorys', {'bill_book': bill_book['_id']})
