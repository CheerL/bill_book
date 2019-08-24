from page import api
import json
from flask import request, jsonify
from flask_cors import cross_origin
from page.encrypt import jwt_run, bcrypt_generator, bcrypt_checker
from data_base import operator


@api.route('/users/register', methods=['POST'])
@cross_origin(supports_credentials=True)
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember', False)
    nickname = request.form.get('nickname')

    # check user
    user = operator.get('users', {'username': username})
    if user:
        return jsonify({
            'status': False,
            'msg': 'User already exists'
        }), 409

    # create user_info
    user_info = operator.post('user_infos', {'nickname': nickname})
    if not user_info:
        return jsonify({
            'status': False,
            'msg': 'Failed to create user info'
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
            'status': False,
            'msg': 'Failed to create user' 
        }), 407

    # create default account
    account = operator.post('accounts', {
        'name': 'default account',
        'amount': 0.0,
        'default': True,
        'user': user_info['_id']
    })
    if not account:
        operator.delete('user_infos', {'_id': user_info['_id']})
        operator.delete('users', {'_id': user['_id']})
        return jsonify({
            'status': False,
            'msg': 'Failed to create account' 
        }), 407

    # generate jwt
    status, msg, jwt, payload = jwt_run(payload={
        'user': user_info['id'],
        'remember': remember
    })
    if not status:
        return jsonify({
            'status': False,
            'msg': msg
        }), 400

    return jsonify({
        'status': True,
        'user': user_info['id'],
        'jwt': jwt,
        'msg': msg
    }), 200

@api.route('/users/login', methods=['POST', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def login():
    data = json.loads(request.get_data())
    # data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    remember = data.get('remember', False)
    # get user
    user = operator.get('users', {'username': username})
    if not user:
        return jsonify({
            'status': False,
            'msg': 'User does not exist'
        }), 401

    # check password
    if not bcrypt_checker(password, user['password']):
        return jsonify({
            'status': False,
            'msg': 'Password is wrong'
        }), 401

    # get user info
    user_info = operator.get('user_infos', {'_id': user['info']})
    if not user_info:
        return jsonify({
            'status': False,
            'msg': 'Failed to get user information'
        }), 404

    # generate jwt
    status, msg, jwt, payload = jwt_run(payload={
        'user': user_info['id'],
        'remember': remember
    })
    if not status:
        return jsonify({
            'status': False,
            'msg': msg
        }), 400

    return jsonify({
        'status': True,
        'jwt': jwt,
        'msg': msg,
        'user': user_info['id']
    }), 200

@api.route('/users/remove', methods=['POST'])
@cross_origin(supports_credentials=True)
def remove():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = request.form.get('remember', False)

    # get user
    user = operator.get('users', {'username': username})
    if not user:
        return jsonify({
            'status': False,
            'msg': 'User does not exist'
        }), 401

    # check password
    if not bcrypt_checker(password, user['password']):
        return jsonify({
            'status': False,
            'msg': 'Password is wrong'
        }), 401

    # get user info
    user_info = operator.get('user_infos', {'_id': user['info']})

    if user_info:
        # remove bill books
        # TODO
        # if there are other owners, remove user from owner list
        # if user not owners, remove user from corrensponding list
        operator.delete_many('bill_books', {
            '_id': {'$in': user_info.get('bill_books', [])},
            'owners': [user_info['_id']]
        })
        

        # TODO
        # remove the avator if it was saved

        # remove user info
        operator.delete('user_infos', {'_id': user_info['_id']})

    # remove account
    operator.delete_many('accounts', {'user': user_info['_id']})

    operator.delete('users', {'_id': user['_id']})

    return jsonify({
        'status': True,
        'msg': 'remove user'
    }), 200

@api.route('/users/reset_password', methods=['POST'])
@cross_origin(supports_credentials=True)
def reset_password():
    username = request.form.get('username')
    new_password = request.form.get('new_password')

    # get user
    user = operator.get('users', {'username': username})
    if not user:
        return jsonify({
            'status': False,
            'msg': 'User does not exist'
        }), 401

    # save new password
    hashed = bcrypt_generator(new_password)
    operator.patch('users', {'$set': {'password': hashed}}, {'_id': user['_id']})

    return jsonify({
        'status': True,
        'msg': 'OK'
    }), 200

