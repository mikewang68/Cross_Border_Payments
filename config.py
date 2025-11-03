import os
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 数据库配置
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '971112')
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_DATABASE = os.getenv('DB_DATABASE', 'gsalary')

# N8N聊天助手URL配置
N8N_CHAT_URL = os.getenv('N8N_CHAT_URL', 'http://localhost:5678/webhook/aa9571f3-5576-4f00-8150-b65c5cabea33/chat')

# 其他配置
DATABASE_URL = os.getenv('DATABASE_URL', '')
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
GSALARY_API_URL = os.getenv('GSALARY_API_URL', 'https://api.gsalary.com')

# Flask配置
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
