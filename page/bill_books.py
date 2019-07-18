from auth import BaseAuth
from data_base import operator
from page.common import abort, get_data, set_data, del_immutable_field
from page.bill_book_user_relation import get_user_bill_book_relation, check_bill_book_lookup

class BillBookAuth(BaseAuth):
    def instance_auth(self, bill_book, method):
        user = get_data('user')
        if not user:
            return False

        relation = operator.get(
            'bill_book_user_relation',
            {'user': user['_id'], 'bill_book': bill_book['_id']}
        )
        if relation:
            set_data('relation', relation)
            relation_status = relation['status']
        else:
            relation_status = 4

        bill_book_status = bill_book['status']
        if method == 'DELETE':
            return relation_status <= 0
        elif method == 'PATCH':
            return relation_status <= 1
        elif method == 'GET':
            return bill_book_status <= 1 or relation_status <= 3
        return False

    def resource_auth(self, method):
        return True

# C
# def pre_insert_bill_books(bill_books):
#     user = get_data('user', 409)
#     for num, bill_book in enumerate(bill_books):
#         bill_books[num]['owners'] = [user['_id']]

def post_insert_bill_books(bill_books):
    '''
    After insert bill_books, for each bill_book:
        1. Set now user as owner
    '''
    user = get_data('user', 409)
    for bill_book in bill_books:
        operator.post('bill_book_user_relation', {
            'user': user['_id'],
            'bill_book': bill_book['_id'],
            'status': 0
        })

# R
def pre_get_bill_books(req, lookup):
    '''
    Before get bill_books, check lookup to make sure
    users can only view accessible bill books:
        1. If not specified bill books, limit the range as
           user's bill book.
        2. Given one bill book, continue if user have view privileges,
           otherwise stop with error 409
        3. Given many bill book, check each and remove unaccessible ones.
    '''
    user = get_data('user', 409)
    relation = get_user_bill_book_relation(user['_id'])
    # print
    bill_book = lookup.get('_id', None) 

    if bill_book:
        lookup['_id'] = check_bill_book_lookup(bill_book, user['_id'], relation)
    else:
        lookup['_id'] = {'$in': list(relation.keys())}
    # print(lookup)

# U
def pre_update_bill_books(updates, bill_book):
    '''
    Before update bill book:
        1. Only bill book's owners can change its status
    '''
    print(updates)
    if 'status' in updates:
        relation = get_data('relation', 400)
        if relation['status'] > 0:
            del updates['status']

# D
def post_delete_bill_books(bill_book):
    '''
    After delete bill book:
        1. Clear all relation between this book and users.
        2. Delete all bills belonging to this book.
        3. Delete all bill categorys belonging to this book.
    '''
    operator.delete_many('bill_book_user_relation', {'bill_books': bill_book['_id']})
    operator.delete_many('bills', {'bill_book': bill_book['_id']})
    operator.delete_many('bill_categorys', {'bill_book': bill_book['_id']})
