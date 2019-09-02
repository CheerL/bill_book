from auth import BaseAuth
from data_base import operator
from page.common import abort, get_data, set_data, del_immutable_field


class BillBookUserRelationAuth(BaseAuth):
    def instance_auth(self, relation, method):
        user = get_data('user')
        if not user:
            return False

        user_relation = operator.get('billbook_user_relation', {
            'user': user['_id'],
            'billbook': relation['billbook']
        })
        set_data('relation', user_relation)

        if method in ['DELETE', 'PATCH']:
            return user_relation and user_relation['status'] <= 1
        elif method == 'GET':
            return True
        return False

    def resource_auth(self, method):
        return True


def get_user_billbook_relation(user, with_transfer=False):
    relations = operator.get_many(
        'billbook_user_relation',
        {'user': user}
    )
    relation_dict = {}
    for relation in relations:
        if not with_transfer:
            billbook = operator.get('billbooks', {'_id': relation['billbook']})
            if billbook['name'] == '***transfer***':
                continue
        relation_dict[relation['billbook']] = relation['status']
    # relations = {
    #     relation['billbook']:relations['status']
    #     for relation in relations
    # }
    return relation_dict

def get_transfer_billbook(user):
    relations = operator.get_many(
        'billbook_user_relation',
        {'user': user}
    )
    for relation in relations:
        billbook = operator.get('billbooks', {'_id': relation['billbook']})
        if billbook['name'] == '***transfer***':
            return billbook['_id']

def check_billbook_readable(billbook, user, relation=None):
    billbook = operator.get('billbooks', {'_id': billbook})
    status = billbook.get('status')
    if status <= 1:
        return True
    elif relation is not None:
        return billbook['_id'] in relation
    else:
        relation = operator.get(
            'billbook_user_relation',
            {'user': user, 'billbook': billbook['_id']}
        )
        return relation is not None
    return False


def check_billbook_lookup(billbook_lookup, user, relation=None):
    if relation is None:
        relation = get_user_billbook_relation(user)

    if isinstance(billbook_lookup, dict):
        billbooks = billbook_lookup.get('$in', [])
        remove_books = []
        for billbook in billbooks:
            if not check_billbook_readable(billbook, user, relation):
                remove_books.append(billbook)

        billbooks = [
            billbook for billbook in billbooks
            if billbook not in remove_books
        ]
        billbook_lookup = {'$in': billbooks}
    elif not check_billbook_readable(billbook_lookup, user, relation):
        abort(409)
    return billbook_lookup

# C
def pre_insert_relation(relations):
    '''
    Before insert relation:
        1. Only owners or managers can add new user.
        2. Managers can only add writers or readers
    '''
    user = get_data('user', 409)
    for num, relation in enumerate(relations):
        user_relation = operator.get('billbook_user_relation', {
            'user': user['_id'],
            'billbook': relation['billbook']
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
    if lookup.get('_id', None) is None:
        user = get_data('user', 409)

        billbook = lookup.get('billbook', None)
        user_ = lookup.get('user', None)
        if not billbook and not user_:
            lookup['user'] = user['_id']
        elif billbook and not user_:
            lookup['billbook'] = check_billbook_lookup(billbook, user['_id'])
        elif not billbook and user_ and user_ != user['_id']:
            pass
