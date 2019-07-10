from app import app
from page import api

import page.users
import page.bill_books
import page.accounts

app.register_blueprint(api, url_prefix=app.api_prefix)
app.on_inserted_bill_books += page.bill_books.post_insert_bill_books
app.on_deleted_item_bill_books += page.bill_books.post_delete_bill_books
app.on_delete_item_accounts += page.accounts.pre_delete_accounts
app.on_update_accounts += page.accounts.pre_patch_accounts

if __name__ == '__main__':
    app.run()
