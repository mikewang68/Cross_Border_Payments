from flask import Flask
from blueprints.auth import bp as auth_bp
from blueprints.query import bp as query_bp
import config
from exts import db,mail

app = Flask(__name__)

app.config.from_object(config)

db.init_app(app)
mail.init_app(app)

app.register_blueprint(auth_bp)

app.register_blueprint(query_bp)


if __name__ == '__main__':
    app.run(debug=True)
