# 项目配置文件

# 数据库的配置信息
HOSTNAME = '8.213.144.235'
PORT     = '3306'
DATABASE = 'gtest'
USERNAME = 'gtest'
PASSWORD = '971112'
DB_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI
SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用对象修改追踪，提升性能
