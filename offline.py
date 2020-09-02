class Group:
    class Payment:    #交易记录
        def __init__(self,t=None,aux=None):
            self.type = t
            self.aux = aux

    class Input:    #记录当前用户信息，含本轮交易记录、当前余额、未完成的条件支付
        def __init__(self,p=None,b=None,c=set()):
            self.pay = p
            self.balance = b
            self.conpay = c

    class State:    #状态，包括所有人的状态和余额及签名
        def __init__(self):
            self.r = -1
            self.inputs = []
            self.signs = []
            self.fee = -1
            self.cus_sign = None

#---------------------------------------------------------------------

    def __init__(self,n):
        self.n = n    #人数
        self.states = []    #所有轮次的状态


        tmp_state = []
        
        tmp_r = 0    #轮次
        tmp_input = []    #所有人的用户信息（内含交易记录、余额、未完成支付）
        tmp_sign = []    #交易记录对应的签名
        tmp_f = 0    #手续费
        tmp_cussign = None    #custodian签名
        for i in range(n):
            tmp_input.append(Input(None,1000))    #初始余额1000
            tmp_sign.append(None)    #初始签名

        tmp_state = [tmp_r,tmp_input,tmp_sign,tmp_f]    #state结构
        self.states.append(tmp_state)

    

    def get_input(self,zround,zidx):    #获取第round轮中，第idx名用户的用户信息input
        return self.states[zround-1].inputs[zidx]

    def get_pay(self,zround,zidx):    #获取第round轮中，第idx名用户的交易记录pay
        return self.states[zround-1].inputs[zidx].pay

    def get_balance(self,zround,zidx):    #获取第round轮中，第idx名用户的余额
        return self.states[zround-1].inputs[zidx].balance

    def node_update_one(self,zround,zidx):    #更新第round轮中，第idx名用户的数据，返回Input
        #Input类中，payment已有，该函数负责更新balance和conpay数据
        zpay = self.get_pay(zround,zidx)    #本轮的payment数据
        zinput = self.get_input(zround,zidx)    #本轮的input数据，将结果写入
        
        if zpay.type == 'dirp':    #直接支付，aux = (pr付款,pe收款,amt金额)
            pr = zpay.aux[0]
            pe = zpay.aux[1]
            amt = zpay.aux[2]
            if zpay.round == r and self.get_balance(zround-1,pr) >= amt:
                if pr == zidx:    #自己是付款方
                    balance = self.get_balance(zround-1,pr) - amt
                elif pe == zidx:    #自己是收款方
                    balance = self.get_balance(zround-1,pe) + amt
                else:
                    print('Error')
                zinput.balance = balance
                
        elif zpay.type == 'conp':
            pr = zpay.aux[0]
            pe = zpay.aux[1]
            amt = zpay.aux[2]
            if zpay.round == r and self.get_balance(zround-1,pr) >= amt:
                if pr == zidx:    #自己是付款方
                    balance = self.get_balance(zround-1,pr) - amt
                    conpay = set(zinput.conpay)
                    conpay.add(pay)
                elif pe == zidx:    #自己是收款方
                    balance = self.get_balance(zround-1,pe) - 0
                    conpay = set(zinput.conpay)
                    conpay.add(pay)
                else:
                    print('Error')
                zinput.balance = balance
                zinput.conpay = conpay
                    
        elif pay.type == 'fulp':
            cmd = zpay.aux[0]
            cpay = zpay.aux[1]
            if zpay.round == r and cpay in cpay in ? & ?:
                ? = ?.remove(cpay)
                ? = ?.remove(cpay)
                if cmd == 'complete':
                    ?
                    ?
                elif cmd == 'cancel':
                    ?
                    ?
                else:
                    print('Error')

                    
        else:
            pass

        ?
        ?
        return ?

    def update(self):
        
