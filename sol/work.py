from web3 import Web3, HTTPProvider
import web3
from easysolc import Solc
import json
import copy
from coincurve import PrivateKey
from zsign import *

s_keys = []
p_keys = []
addr = []
dat1 = None
dat2 = None
state_dat1 = None
state_dat2 = None

class Payment:
    def __init__(self):
        self.round = 0
        self.pr = 0
        self.pe = 0
        self.amount = 0
        
class Input:
    def __init__(self):
        self.pay = Payment()
        self.balance = 0

class State:
    def __init__(self):
        self.r = 0
        self.inputs = []
        self.F = 0

def gen_state(name):
    pay = []
    ans = State()
    with open(name, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            tmp = line.split()
            for i in range(len(tmp)):
                tmp[i] = int(tmp[i])

            if len(tmp) == 2:
                ans.r = tmp[0]
                ans.F = tmp[1]
                continue
            
            ans.inputs.append(Input())
            ans.inputs[-1].pay.round = tmp[0]
            ans.inputs[-1].pay.pr = tmp[1]
            ans.inputs[-1].pay.pe = tmp[2]
            ans.inputs[-1].pay.amount = tmp[3]
            ans.inputs[-1].balance = tmp[4]
    return ans

def state_to_bytes(zstate):
    global s_keys,p_keys
    ans = bytes()
    
    for i in range(len(zstate.inputs)):
        zinput = zstate.inputs[i]
        r = (zinput.pay.round).to_bytes(4, byteorder='big')
        pr = (zinput.pay.pr).to_bytes(2, byteorder='big')
        pe = (zinput.pay.pe).to_bytes(2, byteorder='big')
        amount = (zinput.pay.amount).to_bytes(6, byteorder='big')
        balance = (zinput.balance).to_bytes(6, byteorder='big')
        tmp = r + pr + pe + amount + balance

        p, pk = s_keys[i], p_keys[i]
        h_msg = b_hasher(tmp)
        sig_msg = b_sign_recoverable(h_msg, p)
        
        ans += tmp + bytes.fromhex(sig_msg)
        
    r = (zstate.r).to_bytes(4, byteorder='big')
    F = (zstate.F).to_bytes(6, byteorder='big')
    ans += r + F

    
    p, pk = s_keys[0], p_keys[0]
    h_msg = b_hasher(ans)
    sig_msg = b_sign_recoverable(h_msg, p)

    ans += bytes.fromhex(sig_msg)
    return ans

def get_key():
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

def s_compile(send):
    solc = Solc()
    # 编译智能合约并放在当前目录
    solc.compile('work.sol', output_dir='.')

    if send != True:
        return
    
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

def s_connect(contractAddr):
    global addr
    w3 = Web3(HTTPProvider("http://localhost:8545"))
    w3.eth.defaultAccount = w3.eth.accounts[0]
    w3.eth.defaultBlock = "latest"
    
    abi = loadJson('work.abi')
    bytecode = loadBin('work.bin')
    contract = w3.eth.contract(address=contractAddr,abi=abi)
    
    return contract

def s_add_users(deployed,data):
    b = bytes()
    for obj in data:
        b += bytes.fromhex(obj[2::])
        print(len(b))
    tx_hash = deployed.functions.add_user(b).transact()

def s_zAudit(deployed,zstate):
    b = state_to_bytes(zstate)
    print(len(b))
    return deployed.functions.zAudit(b).call()

def s_record(deployed,pos):
    return deployed.functions.record(pos).call()

def s_sbs(deployed,zstate):
    b = state_to_bytes(zstate)
    print(len(b))
    return deployed.functions.set_beststate(b).transact()

def get_data3(deployed):
    return deployed.functions.get_data3().call()

def init():
    get_key()

def main():
##    s_compile(True)
##    return
    
    global addr
    get_key()
    state = gen_state('init2.txt')
##    state.inputs[1].balance += 1
    deployed = s_connect('0x649bBb00f03dcE57de80D1318c865379dAE0E4E3')
    print(len(state_to_bytes(state)))

##    s_add_users(deployed,addr)
##    s_sbs(deployed,state)
    print(s_zAudit(deployed,state))

    pass
    
  
main()
