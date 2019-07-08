from app import app
from page import api

import page.users

app.register_blueprint(api, url_prefix=app.api_prefix)

if __name__ == '__main__':
    app.run()
