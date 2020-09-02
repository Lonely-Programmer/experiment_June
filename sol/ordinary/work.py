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

def input_hash(zinput):
    r = (zinput.pay.round).to_bytes(4, byteorder='big')
    pr = (zinput.pay.pr).to_bytes(2, byteorder='big')
    pe = (zinput.pay.pe).to_bytes(2, byteorder='big')
    amount = (zinput.pay.amount).to_bytes(6, byteorder='big')
    balance = (zinput.balance).to_bytes(6, byteorder='big')
    ans = r + pr + pe + amount + balance
    ans = b_hasher(ans)
    return ans

def state_hash(zstate):
    r = (zstate.r).to_bytes(4, byteorder='big')
    ans = r
    for i in range(len(zstate.inputs)):
        ans += input_hash(zstate.inputs[i])
    F = (zstate.F).to_bytes(6, byteorder='big')
    ans += F
    ans = b_hasher(ans)
    return ans

def zsign_all(zstate):
    global s_keys,p_keys
    ans = []
    for i in range(len(zstate.inputs)):
        p, pk = s_keys[i], p_keys[i]
        h_msg = input_hash(zstate.inputs[i])
        sig_msg = b_sign_recoverable(h_msg, p)
        ans.append(sig_msg)

    p, pk = s_keys[0], p_keys[0]
    h_msg = state_hash(zstate)
    sig_msg = b_sign_recoverable(h_msg, p)
    ans.append(sig_msg)
    
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
    for obj in data:
        tx_hash = deployed.functions.add_user(Web3.toChecksumAddress(obj)).transact()

def s_set_input_all(deployed,zstate,pos):  
    for i in range(len(zstate.inputs)):
        zinput = zstate.inputs[i]
        deployed.functions.set_input(pos,i,zinput.pay.round,zinput.pay.pr,zinput.pay.pe,zinput.pay.amount,zinput.balance).transact()
    deployed.functions.set_round_F(pos,zstate.r,zstate.F).transact()

def s_set_input_all_b(deployed,zstate,pos):  
    for i in range(len(zstate.inputs)):
        zinput = zstate.inputs[i]
        deployed.functions.set_input_b(pos,i,zinput.pay.round,zinput.pay.pr,zinput.pay.pe,zinput.pay.amount,zinput.balance).transact()
    #deployed.functions.set_round_F(pos,zstate.r,zstate.F).transact()

def s_set_sign(deployed,zstate,pos):
    dat = zsign_all(zstate)
    for i in range(len(dat)-1):
        deployed.functions.set_input_sig(pos,i,dat[i]).transact()
    deployed.functions.set_state_sig(pos,dat[-1]).transact()

def s_verify_input(deployed,pos,zid):
    return deployed.functions.verify_input(pos,zid).call()

def s_verify_state(deployed,pos):
    return deployed.functions.verify_state(pos).call()

def s_verify_sgn(deployed,pos):
    return deployed.functions.verify_sgn(pos).transact()

def s_AuditSin(deployed,pos):
    return deployed.functions.AuditSin(pos).call()

def s_AuditDou(deployed,pos):
    return deployed.functions.AuditDou(pos).call()

def s_Audit(deployed,pos):
    return deployed.functions.Audit(pos).transact()

def s_record(deployed,pos):
    return deployed.functions.record(pos).transact()

def s_sbs(deployed,pos):
    return deployed.functions.set_beststate(pos).transact()

def get_data3(deployed):
    return deployed.functions.get_data3().call()

def init():
    get_key()

def main():
    s_compile(False)
    return

    
    get_key()
    state = gen_state('init.txt')
    sign = zsign_all(state)
    deployed = s_connect('0x98F430B3578f6e9119155dd136bAB741E13939F9')
    global addr

##    print(state.r)
##    s_add_users(deployed,addr)
##    s_set_input_all(deployed,state,1)
##    
##    s_set_sign(deployed,state,1)

##    for i in range(10):
##        print(s_verify_input(deployed,1,i))
##    print(s_verify_state(deployed,1))
    
##    print(s_AuditSin(deployed,1))
##    s_set_input_all_b(deployed,state,1)
##    print(s_AuditSin(deployed,1))
##    print(s_AuditDou(deployed,1))
##    print(s_Audit(deployed,1))
##    print(s_verify_sgn(deployed,1))
##    print(s_record(deployed,1))
    print(s_sbs(deployed,1))
##    print(get_data3(deployed))
    pass
    
  
main()
