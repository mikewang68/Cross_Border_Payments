import hashlib
import base58

def generate_key(email):
    # 步骤1：
    combined_data = email

    # 步骤2：使用SHA-256哈希
    sha256_hash = hashlib.sha256(combined_data.encode('utf-8')).digest()

    # 步骤3：使用RIPEMD-160哈希
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    # 步骤4：使用Base58编码
    base58_encoded = base58.b58encode(ripemd160_hash).decode('utf-8')

    return base58_encoded


