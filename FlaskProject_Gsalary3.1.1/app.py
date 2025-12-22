from flask import Flask

from blueprints.physical_card import bp as physical_card_bp
from blueprints.auth import bp as auth_bp
from blueprints.query import bp as query_bp

app = Flask(__name__)

app.register_blueprint(auth_bp)

app.register_blueprint(query_bp)

app.register_blueprint(physical_card_bp)


if __name__ == '__main__':
    app.run(debug=True)
