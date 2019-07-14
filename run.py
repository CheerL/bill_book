from app import app
from page import api
from settings import HOST, PORT

import page.users
import page.bill_books
import page.accounts
import page.bills
import page.bill_categorys
import page.bill_book_user_relation
import page.common


app.register_blueprint(api, url_prefix=app.api_prefix)

app.on_update += page.common.pre_update

app.on_insert_accounts += page.accounts.pre_insert_accounts
app.on_pre_GET_accounts += page.accounts.pre_get_accounts
app.on_update_accounts += page.accounts.pre_update_accounts
app.on_delete_item_accounts += page.accounts.pre_delete_accounts
app.on_deleted_item_accounts += page.accounts.post_delete_accounts

app.on_inserted_bills += page.bills.post_insert_bills
app.on_pre_GET_bills += page.bills.pre_get_bills
app.on_update_bills += page.bills.pre_update_bills
app.on_deleted_bills += page.bills.post_delete_bills

# app.on_insert_bill_books += page.bill_books.pre_insert_bill_books
app.on_inserted_bill_books += page.bill_books.post_insert_bill_books
app.on_pre_GET_bill_books += page.bill_books.pre_get_bill_books
app.on_pre_update_bill_books += page.bill_books.pre_update_bill_books
app.on_deleted_item_bill_books += page.bill_books.post_delete_bill_books

app.on_insert_bill_book_user_relation += page.bill_book_user_relation.pre_insert_relation
app.on_pre_GET_bill_book_user_relation += page.bill_book_user_relation.pre_insert_relation

app.on_insert_bill_categorys += page.bill_categorys.pre_insert_bill_categorys
app.on_pre_GET_bill_categorys += page.bill_categorys.pre_get_cats
app.on_update_bill_categorys += page.bill_categorys.pre_update_bill_categorys
app.on_deleted_item_bill_categorys += page.bill_categorys.post_delete_bill_categorys

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)

