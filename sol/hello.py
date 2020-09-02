from web3 import Web3, HTTPProvider
import web3
from easysolc import Solc #放在文件最上面
import json
import sha3

#签名工具函数
    
def hasher(msg_str):
    k = sha3.keccak_256()
    k.update(msg_str.encode("utf-8"))
    return k.hexdigest()

def hash2hex(msg):
    return bytes(bytearray.fromhex(msg))


def sign_recoverable(hash_msg_str, pk_str):
    from coincurve import PrivateKey
    pk = PrivateKey(bytearray.fromhex(pk_str))
    return pk.sign_recoverable(hash2hex(hash_msg_str), hasher=None).hex()


def from_signature_and_message(sig_msg_str, msg_str):
    from coincurve import PublicKey
    pk = PublicKey.from_signature_and_message(bytes(bytearray.fromhex(sig_msg_str)), bytes(bytearray.fromhex(msg_str)),
                                              hasher=None)
    return pk.format(compressed=False).hex()


def pk2address(pk_str):
    k = sha3.keccak_256()
    k.update(bytes(list(hash2hex(pk_str))[1:]))
    return bytes(k.digest()[12:]).hex()

def get_key():
    #w3 = Web3(HTTPProvider("http://localhost:8545"))
    #w3.eth.defaultAccount = w3.eth.accounts[0]
    #print(w3.eth.accounts[0])
    from coincurve import PrivateKey
    s_keys = []
    p_keys = []
    with open('keys.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            p = PrivateKey(bytearray.fromhex(line))
            s_keys.append(line)
            p_keys.append(p.public_key.format(compressed=False).hex())
            
            #print(type(p))
            #print([p.to_hex(), p.public_key.format(compressed=False).hex()])
    return (s_keys[0],p_keys[0])

#

def zsign(s):
    p, pk = get_key()
    msg = s
    h_msg = hasher(msg)
    sig_msg = sign_recoverable(h_msg, p)
    print(from_signature_and_message(sig_msg, h_msg) == pk)
    print(pk2address(pk))
    return (h_msg,sig_msg)

def loadJson(file):
    f = open(file, encoding='utf-8')  #设置以utf-8解码模式读取文件，encoding参数必须设置，否则默认以gbk模式读取文件，当文件中包含中文时，会报错
    ans = json.load(f)
    return ans

def loadBin(file):
    f = open(file, 'r', encoding='utf-8')
    ans = f.read()
    return ans

def s_compile():
    solc = Solc()
    # 编译智能合约并放在当前目录
    solc.compile('sign.sol', output_dir='.')
    #return
    
    w3 = Web3(HTTPProvider("http://localhost:8545")) #有疑问请看web3.py官网
    w3.eth.defaultAccount = w3.eth.accounts[0]    #使用账户0来部署。
    
    # 获取智能合约实例 其中abi和bin文件为编译后生成的文件，可以去你的项目目录下找。
    contract = solc.get_contract_instance(w3=w3, abi_file='sign.abi', bytecode_file='sign.bin') 
    # 部署智能合约
    tx_hash = contract.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)#等待挖矿过程
    # 获得智能合约部署在链上的地址
    contractAddr = tx_receipt.contractAddress

def s_exec1():
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    s = "hello"
    h,s = zsign(s)
    print(type(h),type(s))

    contractAddr = '0x75B4fB2391b990232d83288995a8AcF814957f13'

    abi = loadJson('Sign.abi')
    bytecode = loadBin('Sign.bin')
    
    deployed = w3.eth.contract(address=contractAddr,abi=abi)
    ans = deployed.functions.look().call()
    print(h)
    print(ans)
    #print(ans.hex())
    #print(deployed.functions.recover(h,s).call())

def s_exec():
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    contractAddr = '0x75B4fB2391b990232d83288995a8AcF814957f13'
    fromAddr = '0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14'

    gasPrice = w3.eth.gasPrice

    abi = loadJson('Sign.abi')
    bytecode = loadBin('Sign.bin')
    priv_key = '8514d98bdabc1bf2153cab0946e9cbd2edc6c486c0369d7a917aac4ba8c63c08'

    contract = w3.eth.contract(address=contractAddr,abi=abi)
    count = w3.eth.getTransactionCount(fromAddr)

    tx_hash = contract.functions.add(4,6,8).transact()
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    print("Transaction receipt mined:")
    print(dict(receipt))
    print("\nWas transaction successful?")
    print(receipt["status"])

def main():
    #s_exec()
    s_exec1()
    #s_compile()
    #zsign()
    
main()
