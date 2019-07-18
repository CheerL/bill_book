from auth import BaseAuth
from data_base import operator
from page.common import abort, get_data, set_data, del_immutable_field


class BillBookUserRelationAuth(BaseAuth):
    def instance_auth(self, relation, method):
        user = get_data('user')
        if not user:
            return False

        user_relation = operator.get('bill_book_user_relation', {
            'user': user['_id'],
            'bill_book': relation['bill_book']
            })
        set_data('relation', user_relation)

        if method in ['DELETE', 'PATCH']:
            return user_relation and user_relation['status'] <= 1
        elif method == 'GET':
            return True
        return False

    def resource_auth(self, method):
        return True


def get_user_bill_book_relation(user):
    relations = operator.get_many(
        'bill_book_user_relation',
        {'user': user}
    )
    relation_dict = {}
    for relation in relations:
        relation_dict[str(relation['bill_book'])] = relation['status']
    # relations = {
    #     relation['bill_book']:relations['status']
    #     for relation in relations
    # }
    return relation_dict

def check_bill_book_readable(bill_book, user, relation=None):
    bill_book = operator.get('bill_books', {'_id': bill_book})
    status = bill_book.get('status')
    if status <= 1:
        return True
    elif relation is not None:
        return operator.id2str(bill_book['_id']) in relation
    else:
        relation = operator.get(
            'bill_book_user_relation',
            {'user': user, 'bill_book': bill_book['_id']}
        )
        return relation is not None
    return False

def check_bill_book_lookup(bill_book_lookup, user, relation=None):
    if relation is None:
        relation = get_user_bill_book_relation(user)

    if isinstance(bill_book_lookup, dict):
        bill_books = bill_book_lookup.get('$in', [])
        remove_books = []
        for bill_book in bill_books:
            if not check_bill_book_readable(bill_book, user, relation):
                remove_books.append(bill_book)

        bill_books = [
            bill_book for bill_book in bill_books
            if bill_book not in remove_books
        ]
        bill_book_lookup = {'$in': bill_books}
    elif not check_bill_book_readable(bill_book_lookup, user, relation):
        abort(409)
    return bill_book_lookup

# C
def pre_insert_relation(relations):
    '''
    Before insert relation:
        1. Only owners or managers can add new user.
        2. Managers can only add writers or readers
    '''
    user = get_data('user', 409)
    for num, relation in enumerate(relations):
        user_relation = operator.get('bill_book_user_relation', {
            'user': user['_id'],
            'bill_book': relation['bill_book']
        })
        if not user_relation or user_relation['status'] > 1:
            abort(409)
        if relation['status'] <= 1 and user_relation['status'] == 1:
            abort(409)

# R
def pre_get_relation(req, lookup):
    '''
    Before get relation:
        1. If no bill book and no user, limit to
           now user.
        2. If bill book but no user, only show books
           which can be accessed by now user.
        3. # TODO If not now user and no bill book,
           only show that user public bill books.
    '''
    user = get_data('user', 409)

    bill_book = lookup.get('bill_book', None)
    user_ = lookup.get('user', None)
    if not bill_book and not user_:
        lookup['user'] = user['_id']
    elif bill_book and not user_:
        lookup['bill_book'] = check_bill_book_lookup(bill_book, user['_id'])
    elif not bill_book and user_ and user_ != user['_id']:
        pass
