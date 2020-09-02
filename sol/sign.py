from web3 import Web3, HTTPProvider
import web3
from easysolc import Solc #放在文件最上面
import json
import sha3


s_keys = []
p_keys = []
addr = []

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

#

def get_key():
    #w3 = Web3(HTTPProvider("http://localhost:8545"))
    #w3.eth.defaultAccount = w3.eth.accounts[0]
    #print(w3.eth.accounts[0])
    from coincurve import PrivateKey
    global s_keys
    global p_keys
    global addr
    s_keys = []
    p_keys = []
    addr = []
    with open('keys.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            p = PrivateKey(bytearray.fromhex(line))
            s_keys.append(line)
            p_keys.append(p.public_key.format(compressed=False).hex())
            addr.append('0x' + pk2address(p_keys[-1]))

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
    return
    
    w3 = Web3(HTTPProvider("http://localhost:8545")) #有疑问请看web3.py官网
    w3.eth.defaultAccount = w3.eth.accounts[0]    #使用账户0来部署。
    
    # 获取智能合约实例 其中abi和bin文件为编译后生成的文件，可以去你的项目目录下找。
    contract = solc.get_contract_instance(w3=w3, abi_file='work.abi', bytecode_file='work.bin') 
    # 部署智能合约
    tx_hash = contract.constructor().transact()
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)#等待挖矿过程
    # 获得智能合约部署在链上的地址
    contractAddr = tx_receipt.contractAddress
    return contractAddr

def s_exec1(contractAddr):
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

##    s = "hello"
##    h,s = zsign(s)
##    print(type(h),type(s))

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    
    deployed = w3.eth.contract(address=contractAddr,abi=abi)
    fromAddr = '0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14'
    #ans = deployed.functions.get_data(fromAddr).call()
    ans = deployed.functions.get_data2(fromAddr).call()
    #print(h)
    print(ans)
    #print(ans.hex())
    #print(deployed.functions.recover(h,s).call())

def s_connect(contractAddr):
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    fromAddr = '0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14'

    gasPrice = w3.eth.gasPrice

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    priv_key = '8514d98bdabc1bf2153cab0946e9cbd2edc6c486c0369d7a917aac4ba8c63c08'

    contract = w3.eth.contract(address=contractAddr,abi=abi)
    count = w3.eth.getTransactionCount(fromAddr)

    #tx_hash = contract.functions.set_input(fromAddr,70,0,fromAddr,fromAddr,3,0,0,10).transact()
    #tx_hash = contract.functions.add_conpay(fromAddr,3,0,fromAddr,fromAddr,20,0,0).transact()
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return contract
    print("Transaction receipt mined:")
    print(dict(receipt))
    print("\nWas transaction successful?")
    print(receipt["status"])

def read_op(name):
    pay = []
    conpay = []
    with open(name, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            tmp = line.split()
            for i in range(1,len(tmp)):
                if len(tmp[i]) < 40:
                    tmp[i] = int(tmp[i])
            if tmp[0] == 'p':
                pay.append(tuple(tmp[1:len(tmp)]))
            elif tmp[1] == 'c':
                conpay.append(tuple(tmp[1:len(tmp)]))

    return (pay,conpay)

def init(contract):
    dat1, dat2 = read_op('init.txt')
    set_inputs(contract,dat1)
    add_conpays(contract,dat2)
    get_key()
    global addr
    add_users(contract,addr)

def compile_init():
    contractAddr = s_compile()
    contract = s_connect(contractAddr)
    print(contract)
    init(contract)

def add_users(contract,data):
    for obj in data:
        tx_hash = contract.functions.add_user(Web3.toChecksumAddress(obj)).transact()

def set_input(contract,data):
    tx_hash = contract.functions.set_input(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9]).transact()
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    #print(receipt["status"])

def set_inputs(contract,data):
    for obj in data:
        set_input(contract,obj)

def add_conpay(contract,data):
    tx_hash = contract.functions.add_conpay(data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]).transact()
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    #print(receipt["status"])

def add_conpays(contract,data):
    for obj in data:
        add_conpay(contract,obj)

def AuditSin(contract,r):
    print(contract.functions.AuditSin(r).call())

def main():
    contractAddr = '0x9ad6D22E3817409Da69C0e635Cc4B0Bfd709e165'
    #compile_init()
    #get_key()
    #read_op('init.txt')
    s_compile()
    #contract = s_connect(contractAddr)
    #set_input(contract,['0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14',0,0,'0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14','0x82a689A037Da019815C11219c66272A5d8c5A495',0,7,0,2,100])
    #set_input(contract,['0x82a689A037Da019815C11219c66272A5d8c5A495',0,0,'0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14','0x82a689A037Da019815C11219c66272A5d8c5A495',0,7,0,2,100])
    #AuditSin(contract,0)
    #init(contract)
    #contract = s_connect(contractAddr)
    #s_exec(contractAddr)
    #s_exec1(contractAddr)
    #s_compile()
    
    #zsign()
    
main()
