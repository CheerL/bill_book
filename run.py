from app import app
from page import api
from settings import HOST, PORT

import page.users
import page.billbooks
import page.accounts
import page.bills
import page.bill_categorys
import page.billbook_user_relation
import page.common


app.register_blueprint(api, url_prefix=app.api_prefix)

app.on_pre_GET += page.common.pre_get
app.on_update += page.common.pre_update

app.on_insert_accounts += page.accounts.pre_insert_accounts
app.on_pre_GET_accounts += page.accounts.pre_get_accounts
app.on_update_accounts += page.accounts.pre_update_accounts
app.on_delete_item_accounts += page.accounts.pre_delete_accounts
# app.on_deleted_item_accounts += page.accounts.post_delete_accounts

app.on_insert_bills += page.bills.pre_insert_bills
app.on_inserted_bills += page.bills.post_insert_bills
app.on_pre_GET_bills += page.bills.pre_get_bills
app.on_fetched_resource_bills += page.bills.post_get_bills
app.on_fetched_item_bills += page.bills.post_get_bills
app.on_update_bills += page.bills.pre_update_bills
app.on_updated_bills += page.bills.post_update_bills
app.on_deleted_item_bills += page.bills.post_delete_bills

app.on_insert_billbooks += page.billbooks.pre_insert_billbooks
app.on_inserted_billbooks += page.billbooks.post_insert_billbooks
app.on_pre_GET_billbooks += page.billbooks.pre_get_billbooks
app.on_update_billbooks += page.billbooks.pre_update_billbooks
app.on_delete_item_billbooks += page.billbooks.pre_delete_billbooks
app.on_deleted_item_billbooks += page.billbooks.post_delete_billbooks

app.on_insert_billbook_user_relation += page.billbook_user_relation.pre_insert_relation
app.on_pre_GET_billbook_user_relation += page.billbook_user_relation.pre_insert_relation

app.on_insert_bill_categorys += page.bill_categorys.pre_insert_bill_categorys
app.on_pre_GET_bill_categorys += page.bill_categorys.pre_get_cats
app.on_update_bill_categorys += page.bill_categorys.pre_update_bill_categorys
app.on_deleted_item_bill_categorys += page.bill_categorys.post_delete_bill_categorys

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)

