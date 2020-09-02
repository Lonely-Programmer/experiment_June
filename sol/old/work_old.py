from web3 import Web3, HTTPProvider
import web3
from easysolc import Solc #放在文件最上面
import json
import sha3
import copy

s_keys = []
p_keys = []
addr = []
dat1 = None
dat2 = None
state_dat1 = None
state_dat2 = None

def empty_cpay_hash():
    tx_type = (0).to_bytes(32, byteorder='big')
    r = (0).to_bytes(32, byteorder='big')
    pr = (0).to_bytes(20, byteorder='big')
    pe = (0).to_bytes(20, byteorder='big')
    amount = (0).to_bytes(32, byteorder='big')
    h = (0).to_bytes(32, byteorder='big')
    time = (0).to_bytes(32, byteorder='big')
    ans = tx_type + r + pr + pe + amount + h + time
    ans = b_hasher(ans)
    ans = b_hasher(ans*8)
    #print(tx_type)
    #print('python:',len(ans))
    return ans

def empty_input_hash():
    tx_type = (0).to_bytes(32, byteorder='big')
    r = (0).to_bytes(32, byteorder='big')
    pr = (0).to_bytes(20, byteorder='big')
    pe = (0).to_bytes(20, byteorder='big')
    amount = (0).to_bytes(32, byteorder='big')
    h = (0).to_bytes(32, byteorder='big')
    time = (0).to_bytes(32, byteorder='big')
    cmd = (2).to_bytes(32, byteorder='big')
    cpay_h = empty_cpay_hash()
    balance = (100).to_bytes(32, byteorder='big')
    ans = tx_type + r + pr + pe + amount + h + time + cmd + cpay_h + balance
    ans = b_hasher(ans)
    return ans

def empty_state_hash():
    r = (0).to_bytes(32, byteorder='big')
    ans = empty_input_hash()
    F = (0).to_bytes(32, byteorder='big')
    ans = r + ans * 10 + F
    ans = b_hasher(ans)
    return ans

def input_hash(zinput):
    tx_type = (zinput[0]).to_bytes(32, byteorder='big')
    r = (zinput[1]).to_bytes(32, byteorder='big')
    pr = zinput[2]
    if pr == 0:
        pr = (zinput[2]).to_bytes(20, byteorder='big')
    pe = zinput[3]
    if pe == 0:
        pe = (zinput[3]).to_bytes(20, byteorder='big')
    amount = (zinput[4]).to_bytes(32, byteorder='big')
    h = (zinput[5]).to_bytes(32, byteorder='big')
    time = (zinput[6]).to_bytes(32, byteorder='big')
    cmd = (zinput[7]).to_bytes(32, byteorder='big')
    cpay_h = empty_cpay_hash()
    balance = (zinput[9]).to_bytes(32, byteorder='big')
    ans = tx_type + r + pr + pe + amount + h + time + cmd + cpay_h + balance
    ans = b_hasher(ans)
    return ans

def state_hash(zstate):
    r = (zstate[0]).to_bytes(32, byteorder='big')
    ans = bytes()
    for i in range(10):
        ans += input_hash(zstate[1][i])
    F = (zstate[2]).to_bytes(32, byteorder='big')
    ans = r + ans + F
    ans = b_hasher(ans)
    return ans


#签名工具函数
    
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
            addr[-1] = Web3.toChecksumAddress(addr[-1])

##def zsign(s):
##    p, pk = get_key()
##    msg = s
##    h_msg = hasher(msg)
##    sig_msg = sign_recoverable(h_msg, p)
##    print(from_signature_and_message(sig_msg, h_msg) == pk)
##    print(pk2address(pk))
##    return (h_msg,sig_msg)

def zsign(b_hash,idx):
    global s_keys,p_keys
    p, pk = s_keys[idx], p_keys[idx]
    h_msg = b_hash
    sig_msg = b_sign_recoverable(h_msg, p)
    #print(from_signature_and_message(sig_msg, h_msg) == pk)
    #print(pk2address(pk))
    return sig_msg

def zsign_all(zstate):
    global s_keys,p_keys
    
    ans = []
    for i in range(10):
        h_msg = input_hash(zstate[1][i])
        p, pk = s_keys[i], p_keys[i]
        sig_msg = b_sign_recoverable(h_msg, p)
        ans.append(sig_msg)
        
    h_msg = state_hash(zstate)
    p, pk = s_keys[0], p_keys[0]
    sig_msg = b_sign_recoverable(h_msg, p)
    ans.append(sig_msg)
    return ans

def empty_cpay_hash():
    tx_type = (0).to_bytes(32, byteorder='big')
    r = (0).to_bytes(32, byteorder='big')
    pr = (0).to_bytes(20, byteorder='big')
    pe = (0).to_bytes(20, byteorder='big')
    amount = (0).to_bytes(32, byteorder='big')
    h = (0).to_bytes(32, byteorder='big')
    time = (0).to_bytes(32, byteorder='big')
    ans = tx_type + r + pr + pe + amount + h + time
    ans = b_hasher(ans)
    ans = b_hasher(ans*8)
    #print(tx_type)
    #print('python:',len(ans))
    return ans

def empty_input_hash():
    tx_type = (0).to_bytes(32, byteorder='big')
    r = (0).to_bytes(32, byteorder='big')
    pr = (0).to_bytes(20, byteorder='big')
    pe = (0).to_bytes(20, byteorder='big')
    amount = (0).to_bytes(32, byteorder='big')
    h = (0).to_bytes(32, byteorder='big')
    time = (0).to_bytes(32, byteorder='big')
    cmd = (2).to_bytes(32, byteorder='big')
    cpay_h = empty_cpay_hash()
    balance = (100).to_bytes(32, byteorder='big')
    ans = tx_type + r + pr + pe + amount + h + time + cmd + cpay_h + balance
    ans = b_hasher(ans)
    return ans

def empty_state_hash():
    r = (0).to_bytes(32, byteorder='big')
    ans = empty_input_hash()
    F = (0).to_bytes(32, byteorder='big')
    ans = r + ans * 10 + F
    ans = b_hasher(ans)
    return ans


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
    solc.compile('work.sol', output_dir='.')
    #return
    
    w3 = Web3(HTTPProvider("http://localhost:8545")) #有疑问请看web3.py官网
    w3.eth.defaultAccount = w3.eth.accounts[0]    #使用账户0来部署。
    
    # 获取智能合约实例 其中abi和bin文件为编译后生成的文件，可以去你的项目目录下找。
    contract = solc.get_contract_instance(w3=w3, abi_file='work.abi', bytecode_file='work.bin') 
    # 部署智能合约

    tx_hash = contract.constructor().transact()#
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)#等待挖矿过程
    # 获得智能合约部署在链上的地址
    contractAddr = tx_receipt.contractAddress
    return contractAddr

def s_exec1(contractAddr):
    global addr
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

##    s = "hello"
##    h,s = zsign(s)
##    print(type(h),type(s))

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    
    deployed = w3.eth.contract(address=contractAddr,abi=abi)
    fromAddr = addr[1]

    #deployed.functions.record(addr[1]).transact()
    print(deployed.functions.record(addr[1]).call())

    
    #ans = deployed.functions.get_data(fromAddr).call()
    #ans = deployed.functions.get_data(fromAddr).call()
    #ans = deployed.functions.verify_input(0,addr[0]).call()
    #print(deployed.functions.hash_conpay(0,addr[0]).call())
    #print(deployed.functions.t1(0,addr[0]).call())
    #print(deployed.functions.t2(0,addr[0]).call())
    #a = deployed.functions.t3(0,addr[0]).call()
    #a = deployed.functions.hash_input(0,addr[0]).call()
    #a = deployed.functions.hash_state(0).call()
    
##    a = empty_state_hash()
##    print('phash:',a)
##    b = zsign(a,1)
##    print(b)
##    deployed.functions.set_state_sig(addr[1],b).transact()
##    print(deployed.functions.get_state_sig(addr[1]).call())
##    print(deployed.functions.verify_state(addr[1]).call())

##    for i in range(10):
##        a = empty_input_hash()
##        print('phash:',a)
##        b = zsign(a,i)
##        print(b)
##        print(deployed.functions.set_input_sig(addr[1],addr[i],b).transact())
##        print(deployed.functions.get_input_sig(addr[1],addr[i]).call())
##        print(deployed.functions.verify_input(addr[1],addr[i]).call())
##    
##    print('L:',len(a))
##    print('sinputh:',a)
    #print(h)
    #print(ans)
    #print(ans.hex())
    #print(deployed.functions.recover(h,s).call())

def s_sign1(contractAddr):
    global addr
    global state_dat1
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    
    deployed = w3.eth.contract(address=contractAddr,abi=abi)
    fromAddr = addr[1]

    signs = zsign_all(state_dat1)
    for i in range(10):
        deployed.functions.set_input_sig(addr[1],addr[i],signs[i]).transact()
        print(i,deployed.functions.verify_input(addr[1],addr[i]).call())

    deployed.functions.set_state_sig(addr[1],signs[10]).transact()
    print(deployed.functions.verify_state(addr[1]).call())


def s_sign2(contractAddr):
    global addr
    global state_dat2
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    
    deployed = w3.eth.contract(address=contractAddr,abi=abi)
    fromAddr = addr[1]

    signs = zsign_all(state_dat2)
    for i in range(10):
        deployed.functions.set_input_sig(addr[1],addr[i],signs[i]).transact()
        print(i,deployed.functions.verify_input(addr[1],addr[i]).call())

    deployed.functions.set_state_sig(addr[1],signs[10]).transact()
    print(deployed.functions.verify_state(addr[1]).call())
    

def s_connect(contractAddr):
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    fromAddr = '0x2742fE6952e60cd494812260c114e4A5657EF7eb'

    gasPrice = w3.eth.gasPrice

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    priv_key = '3ebe6ce39cec0e7737dbcd5da219fdb0f3f2b5dba355cec7f907533bcc2935f1'

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
    global dat1,dat2
    dat1, dat2 = read_op('init.txt')
    set_inputs(contract,dat1)
    add_conpays(contract,dat2)
    get_key()
    global addr
    add_users(contract,addr)

def init2(contract,name):
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"

    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    
    deployed = w3.eth.contract(address=contract,abi=abi)
    fromAddr = addr[1]
    
    global dat1,dat2
    dat1, dat2 = read_op(name)
    set_inputs(deployed,dat1)
    add_conpays(deployed,dat2)
    get_key()
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
    global addr
    tx_hash = contract.functions.set_input(addr[1],data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7],data[8],data[9]).transact()
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    #print(receipt["status"])

def set_inputs(contract,data):
    for obj in data:
        set_input(contract,obj)

def add_conpay(contract,data):
    global addr
    tx_hash = contract.functions.add_conpay(addr[1],data[0],data[1],data[2],data[3],data[4],data[5],data[6],data[7]).transact()
    #receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    #print(receipt["status"])

def add_conpays(contract,data):
    for obj in data:
        add_conpay(contract,obj)

def AuditSin(contract,r):
    print(contract.functions.AuditSin(r).call())

def main():
##    get_key()
##    read_op('init.txt')
##    compile_init()
##    return
    

    global addr
    global state_dat1
    global state_dat2
    get_key()
    cpay_dat1 = [[0,0,0,0,0,0,0]] * 8
    input_dat1 = [0,0,0,0,0,0,0,2,cpay_dat1,100]
    state_dat1 = [0,[input_dat1] * 10,0]

    state_dat2 = copy.deepcopy(state_dat1)
##    state_dat2[1][1][2] = bytes.fromhex(addr[1][2:])
##    state_dat2[1][1][3] = bytes.fromhex(addr[2][2:])
##    state_dat2[1][1][4] = 5
##    state_dat2[1][2][2] = bytes.fromhex(addr[1][2:])
##    state_dat2[1][2][3] = bytes.fromhex(addr[2][2:])
##    state_dat2[1][2][4] = 5
    #print(zsign_all(state_dat2))

    contractAddr = '0x7DAA46Af8974e55F43316362CdBD8c9256662c02'
    init2(contractAddr,'init.txt')
    s_sign1(contractAddr)
    s_exec1(contractAddr)

    return
    
    
    
    #compile_init()

    #read_op('init.txt')
    #s_compile()
    #contract = s_connect(contractAddr)
    #set_input(contract,['0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14',0,0,'0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14','0x82a689A037Da019815C11219c66272A5d8c5A495',0,7,0,2,100])
    #set_input(contract,['0x82a689A037Da019815C11219c66272A5d8c5A495',0,0,'0xCeA93ab53F005Ef6Ba0Ff92dEef6140C6E57cD14','0x82a689A037Da019815C11219c66272A5d8c5A495',0,7,0,2,100])
    #AuditSin(contract,0)
    #init(contractAddr)
    #contract = s_connect(contractAddr)
    #s_exec(contractAddr)
    
    #return
    s_exec1(contractAddr)
    #s_compile()
    
    #zsign()
  
#main()
