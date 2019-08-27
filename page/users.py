from page import api
from flask import request, jsonify
from flask_cors import cross_origin
from page.encrypt import jwt_run, bcrypt_generator, bcrypt_checker
from page.billbook_user_relation import get_user_billbook_relation
from data_base import operator


def check_jwt(request):
    jwt = request.headers.get("Authorization")
    if not jwt:
        return False, (jsonify({
            'message': 'No JWT'
        }), 401)

    status, new, message, jwt, payload = jwt_run(jwt=jwt)
    if not status:
        return False, (jsonify({
            'message': 'Invaild JWT, need to login'
        }), 401)

    return True, (new, message, jwt, payload)


@api.route('/users/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)
    nickname = data.get('nickname')

    # check user
    user = operator.get('users', {'username': username})
    if user:
        return jsonify({
            'message': 'User already exists'
        }), 409

    # create user_info
    user_info = operator.post('user_infos', {'nickname': nickname})
    if not user_info:
        return jsonify({
            'message': 'Failed to create user info'
        }), 407

    # create user with hashed password
    hashed = bcrypt_generator(password)
    user = operator.post('users', {
        'username': username,
        'password': hashed,
        'info': user_info['_id']
    })
    if not user:
        operator.delete('user_infos', {'_id': user_info['_id']})
        return jsonify({
            'message': 'Failed to create user'
        }), 407

    # create default account
    account = operator.post('accounts', {
        'name': '默认账户',
        'amount': 0.0,
        'default': True,
        'user': user_info['_id']
    })
    if not account:
        operator.delete('user_infos', {'_id': user_info['_id']})
        operator.delete('users', {'_id': user['_id']})
        return jsonify({
            'message': 'Failed to create account'
        }), 407

    # creater transfer billbook
    transfer_billbook = operator.post('billbooks', {
        'name': '***transfer***',
        'status': 2,
        'default': False
    })
    operator.post('billbook_user_relation', {
        'user': user_info['_id'],
        'billbook': transfer_billbook['_id'],
        'status': 0
    })
    # generate jwt
    return jsonify({
        'message': 'Success to register'
    }), 200


@api.route('/users/jwt', methods=['POST'])
@cross_origin(supports_credentials=True)
def login_jwt():
    jwt_status, jwt_result = check_jwt(request)
    if not jwt_status:
        return jwt_result

    new, message, jwt, payload = jwt_result
    user_id = payload.get('user')
    username = payload.get('username')
    user_info = operator.get('user_infos', {'_id': user_id})
    if not user_info:
        return jsonify({
            'message': 'Invaild JWT, need to login'
        }), 401

    return jsonify({
        'jwt': jwt if new else '',
        'message': message,
        'id': user_info['id'],
        'username': username,
        'nickname': user_info['nickname'],
        'avatar': user_info['avatar']
    }), 200


@api.route('/users/login', methods=['POST'])
@cross_origin(supports_credentials=True)
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)
    # get user
    user = operator.get('users', {'username': username})
    if not user:
        return jsonify({
            'message': 'User does not exist'
        }), 401

    # check password
    if not bcrypt_checker(password, user['password']):
        return jsonify({
            'message': 'Password is wrong'
        }), 401

    # get user info
    user_info = operator.get('user_infos', {'_id': user['info']})
    if not user_info:
        return jsonify({
            'message': 'Failed to get user information'
        }), 404

    # generate jwt
    status, new, message, jwt, payload = jwt_run(payload={
        'user': user_info['id'],
        'username': username,
        'remember': remember
    })
    if not status:
        return jsonify({
            'message': message
        }), 400

    return jsonify({
        'jwt': jwt if new else '',
        'message': message,
        'id': user_info['id'],
        'username': username,
        'nickname': user_info['nickname'],
        'avatar': user_info['avatar']
    }), 200


@api.route('/users/remove', methods=['POST'])
@cross_origin(supports_credentials=True)
def remove():
    jwt_status, jwt_result = check_jwt(request)
    if not jwt_status:
        return jwt_result

    _, _, _, payload = jwt_result

    # get user
    username = payload.get('username')
    user = operator.get('users', {'username': username})
    if not user:
        return jsonify({
            'message': 'User does not exist'
        }), 401

    # get user info
    user_info = operator.get('user_infos', {'_id': user['info']})
    if user_info:
        # remove bill books
        # TODO
        # if there are other owners, remove user from owner list
        # if user not owners, remove user from corrensponding list
        relations = get_user_billbook_relation(
            operator.id2str(user_info['_id']),
            True
        )
        print(user['_id'], user['info'], relations, list(relations.keys()))
        operator.delete_many('billbooks', {
            '_id': {'$in': list(relations.keys())},
        })
        operator.delete_many('billbook_user_relation', {
            'user': user_info['_id']
        })

        # TODO
        # remove the avator if it was saved

        # remove user info
        operator.delete('user_infos', {'_id': user_info['_id']})

    # remove account
    operator.delete_many('accounts', {'user': user_info['_id']})

    operator.delete('users', {'_id': user['_id']})

    return jsonify({
        'message': 'Success to remove user'
    }), 200


@api.route('/users/forget', methods=['POST'])
@cross_origin(supports_credentials=True)
def forget():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # get user
    user = operator.get('users', {'username': username})
    if not user:
        return jsonify({
            'message': 'User does not exist'
        }), 401

    # save new password
    hashed = bcrypt_generator(password)
    operator.patch('users', {'$set': {'password': hashed}}, {
                   '_id': user['_id']})

    return jsonify({
        'message': 'Success to reset password'
    }), 200
