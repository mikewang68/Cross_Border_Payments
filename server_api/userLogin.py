import hashlib
import base58
from models import UserModel

User = UserModel

def generate_key(email, user_id):
    # 步骤1：将邮箱和用户名合并
    combined_data = email + user_id

    # 步骤2：使用SHA-256哈希
    sha256_hash = hashlib.sha256(combined_data.encode('utf-8')).digest()

    # 步骤3：使用RIPEMD-160哈希
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # 步骤4：使用Base58编码
    base58_encoded = base58.b58encode(ripemd160_hash).decode('utf-8')

    return base58_encoded


