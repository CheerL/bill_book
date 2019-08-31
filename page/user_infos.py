from auth import BaseAuth
from page.common import get_data, del_immutable_field
from page.billbook_user_relation import get_user_billbook_relation
from data_base import operator

class UserInfoAuth(BaseAuth):
    def instance_auth(self, infos, method):
        user = get_data('user')
        if not user:
            return False

        if method == 'PATCH':
            return user['_id'] == infos['_id']
        elif method == 'GET':
            return True
        return False

    def resource_auth(self, method):
        return True


def pre_update_user_infos(updates, info):
    del_immutable_field(updates, ['avatar'])

def post_update_user_infos(updates, info):
    ori_nickname = info['nickname']
    nickname = updates.get('nickname', '')

    if nickname and nickname != ori_nickname:
        user = get_data('user', 409)
        relation = get_user_billbook_relation(user['_id'], True)
        operator.patch_many(
            'bills',
            {'$set': {'creater_name': nickname}},
            {'creater_name': ori_nickname, 'billbook': {'$in': list(relation.keys())}}
        )
