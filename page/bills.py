from auth import BaseAuth
from data_base import operator
from page.bill_categorys import check_cat, create_cat

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

def pre_insert_bills(bills):
    for bill in bills:
        bill_book = bill['bill_book']
        last_cat = None
        for level in range(3):
            cat_name = bill.get('cat_%d' % level, '')
            if not cat_name:
                break

            parent = last_cat['_id'] if last_cat else None
            cat = check_cat(cat_name, level, bill_book, parent)
            if not cat:
                cat = create_cat(cat_name, level, bill_book, parent)
            last_cat = cat
