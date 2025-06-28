from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.Util.Padding import unpad
import binascii
import base64
import rsa
#from rsa.pkcs1 import PKCS1_OAEP
class SecurityDTO:
    def __init__(self):
        self.key = None
        self.iv = None
        self.body = None
        
        
        
        

def rsa_encrypt_oaep(message, pubkey):
    cipher = PKCS1_OAEP.new(pubkey)
    # OAEP填充允许更大灵活性，但需注意密钥长度匹配
    return cipher.encrypt(message)


PUBLIC_KEY_STR = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCR1BmnrfdI/wK3IloIPfAjmr/VzzEyp2GO8srJMoOpIcSXFweBPqLdIIwpbalog47pbcG3PnDuqWvx/Gr/JNsvQ28QkDW8gkp9Ks6Xg5L1Bb2ye65IhLx6tLoBJ85XzFPWLfUghJ95n0grSgWvFlkTMAkc5disnN1vmdQ0aWPfpwIDAQAB"


def decrypt_security_key_hex_by_public_key(hex_str, PUBLIC_KEY_STR):
    """RSA公钥解密十六进制数据"""
    # 导入公钥
    #pub_key = RSA.import_key(public_key_str)
    
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_STR}\n-----END PUBLIC KEY-----"
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    
    encrypted_data = binascii.unhexlify(hex_str)[:48]
    decrypted_key = rsa.encrypt(encrypted_data, pubkey, padding=rsa.Padding.NONE)
    
    print(bytes.hex(decrypted_key))
    return decrypted_key
    
    #decrypted = cipher.encrypt(encrypted_data)


from Crypto.PublicKey import RSA
from Crypto.Util.number import bytes_to_long, long_to_bytes

def rsa_no_padding_encrypt(public_key, plaintext: bytes) -> bytes:
    # 将明文转换为大整数
    m = bytes_to_long(plaintext)
    # 执行模幂运算（公钥指数e，模数n）
    rsa_key = f"-----BEGIN PUBLIC KEY-----\n{PUBLIC_KEY_STR}\n-----END PUBLIC KEY-----"
    
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(rsa_key.encode())
    public_key = RSA.import_key(f'-----BEGIN RSA PRIVATE KEY-----\n{PUBLIC_KEY_STR}\n-----END RSA PRIVATE KEY-----')
  
    c = pow(m, public_key.e, public_key.n)
    # 转换回字节（自动补前导零）
    
    
    return long_to_bytes(c)#.hex()[156:]
    




def decrypt_response_body(encrypted_data_hex, kk):
    """AES解密响应体"""
    # 使用RSA解密获取AES密钥和IV
    encrypted_data_byte = binascii.unhexlify(encrypted_data_hex)
    
    aes_key_iv =rsa_no_padding_encrypt(PUBLIC_KEY_STR, encrypted_data_byte)
    #aes_key_iv = aes_key_iv.encode()
    #aes_key_iv = binascii.unhexlify(aes_key_iv)
        

    aes_key_iv = aes_key_iv[79:]
    aes_key = aes_key_iv[:32]  # 前32字节为AES密钥
    iv = aes_key_iv[32:48]    # 后16字节为IV
    # AES解密
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(kk)
    
    
    # 去除PKCS5填充
    return unpad(decrypted_data, AES.block_size)

# 使用示例
encrypted_hex = ""  #响应体的x-ac-security-key
filename = ""  #要解密的文件


with open(filename, "rb") as file:
    byte_data = file.read()  # 读取全部内容
r=decrypt_response_body(encrypted_hex, byte_data)
print(r.decode())

with open("tpt.json", "w") as f:
    f.write(r.decode())
    print("解密结果已保存到tpt.json")
