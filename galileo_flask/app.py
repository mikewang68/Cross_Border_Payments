from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import config
from exts import db
from models import ExchangeUSDT

app = Flask(__name__)

# test2
# test branch
# test modifed by mikewang
# 将所有的config写入另一个文件，直接加载左右配置，绑定配置文件
app.config.from_object(config)
db.init_app(app)


# 获取数据的路由
@app.route("/fiat-to-usdt")
def fiat_to_usdt():
    # 查询数据
    exchange_data = ExchangeUSDT.query.all()
    # 将数据传递给模板
    return render_template(
        "index.html", active_tab="fiat-to-usdt", exchange_data=exchange_data
    )


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
