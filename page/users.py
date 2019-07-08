from page import api
from flask import request, jsonify, current_app as app
from page.encrypt import jwt_run, bcrypt_generator, bcrypt_checker
from data_base import operator


@api.route('/users/register', methods=['POST'])
def register():
    account = request.form.get('account')
    password = request.form.get('password')
    remember = request.form.get('remember', False)

    user = operator.get('users', {'account': account})
    if user:
        return jsonify({
            'status': False,
            'msg': 'User already exists'
        }), 409

    hashed = bcrypt_generator(password)
    user, code = operator.web_post('users', {
        'account': account,
        'password': hashed
    })

    if code != 201:
        return jsonify({
            'status': False,
            'msg': user['_error']['message'] + str(user['_issues'])
        }), code


    account, code = operator.web_post('accounts', {
        'name': '默认账户'
    })

    if code != 201:
        operator.delete('users', {'_id': user['_id']})
        return jsonify({
            'status': False,
            'msg': account['_error']['message'] + str(account['_issues'])
        }), code


    nickname = request.form.get('nickname', user['_id'][:15])
    user_info, code = operator.web_post('user_infos', {
        'user': user['_id'],
        'nickname': nickname,
        'accounts': [operator.str2id(account['_id'])]
    })

    if code != 201:
        operator.delete('users', {'_id': user['_id']})
        operator.delete('accounts', {'_id': account['_id']})
        return jsonify({
            'status': False,
            'msg': user_info['_error']['message'] + str(user_info['_issues'])
        }), code

    status, msg, jwt, payload = jwt_run(payload={
        'user': user_info['_id'],
        'remember': remember
    })
    if not status:
        return jsonify({
            'status': False,
            'msg': msg
        }), 400

    return jsonify({
        'status': True,
        'user': user_info['_id'],
        'jwt': jwt,
    }), 200

@api.route('/users/login', methods=['POST'])
def login():
    account = request.form.get('account')
    password = request.form.get('password')
    remember = request.form.get('remember', False)

    user = operator.get('users', {'account': account})
    if not user:
        return jsonify({
            'status': False,
            'msg': 'User does not exist'
        }), 401

    if not bcrypt_checker(password, user['password']):
        return jsonify({
            'status': False,
            'msg': 'Password is wrong'
        }), 401

    user_info = operator.get('user_infos', {'user': user['_id']})
    if not user_info:
        return jsonify({
            'status': False,
            'msg': 'Failed to get user information'
        }), 404

    status, msg, jwt, payload = jwt_run(payload={
        'user': user_info['_id'],
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
        'user': user_info['_id']
    }), 200

@api.route('/users/remove', methods=['POST'])
def remove():
    account = request.form.get('account')
    password = request.form.get('password')

    user = operator.get('users', {'account': account})
    if not user:
        return jsonify({
            'status': False,
            'msg': 'User does not exist'
        }), 401

    if not bcrypt_checker(password, user['password']):
        return jsonify({
            'status': False,
            'msg': 'Password is wrong'
        }), 401

    user_info = operator.get('user_infos', {'user': user['_id']})
    if user_info:
        accounts = user_info.get('accounts', [])
        for account in accounts:
            operator.delete('accounts', {'_id': account})

        bill_books = user_info.get('bill_books', [])
        for bill_book in bill_books:
            bill_book_instance = operator.get('bill_books', {'_id': bill_book})
            user_info_objectid = operator.str2id(user_info['_id'])
            owners = bill_book_instance['owners']
            if owners == [user_info_objectid]:
                operator.delete('bill_books', {'_id': bill_book})
            # TODO
            # if there are other owners, remove user from owner list
            # if user not owners, remove user from corrensponding list

        # TODO
        # remove the avator if it was saved

        operator.delete('user_infos', {'_id': user_info['_id']})

    operator.delete('users', {'_id': user['_id']})

    return jsonify({
        'status': True,
        'msg': 'remove user account'
    }), 200
