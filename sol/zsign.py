from coincurve import PrivateKey
import sha3
import json
    
def hasher(msg_str):
    k = sha3.keccak_256()
    k.update(msg_str.encode("utf-8"))
    return k.hexdigest()

def b_hasher(msg_b):
    k = sha3.keccak_256()
    k.update(msg_b)
    return k.digest()

def hash2hex(msg):
    return bytes(bytearray.fromhex(msg))


def sign_recoverable(hash_msg_str, pk_str):
    from coincurve import PrivateKey
    pk = PrivateKey(bytearray.fromhex(pk_str))
    return pk.sign_recoverable(hash2hex(hash_msg_str), hasher=None).hex()

def b_sign_recoverable(b_hash_msg, pk_str):
    from coincurve import PrivateKey
    pk = PrivateKey(bytearray.fromhex(pk_str))
    return pk.sign_recoverable(b_hash_msg, hasher=None).hex()

def from_signature_and_message(sig_msg_str, msg_str):
    from coincurve import PublicKey
    pk = PublicKey.from_signature_and_message(bytes(bytearray.fromhex(sig_msg_str)), bytes(bytearray.fromhex(msg_str)),
                                              hasher=None)
    return pk.format(compressed=False).hex()


def pk2address(pk_str):
    k = sha3.keccak_256()
    k.update(bytes(list(hash2hex(pk_str))[1:]))
    return bytes(k.digest()[12:]).hex()

def loadJson(file):
    f = open(file, encoding='utf-8')  #设置以utf-8解码模式读取文件，encoding参数必须设置，否则默认以gbk模式读取文件，当文件中包含中文时，会报错
    ans = json.load(f)
    return ans

def loadBin(file):
    f = open(file, 'r', encoding='utf-8')
    ans = f.read()
    return ans
