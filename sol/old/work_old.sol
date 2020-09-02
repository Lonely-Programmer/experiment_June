pragma solidity ^0.6.0;

contract work {

   struct Cpay {
      uint tx_type;
      uint round;
      address pr;
      address pe;
      uint amount;
      uint h;
      uint time;
   }

   struct Payment {
      uint tx_type;
      uint round;
      address pr;
      address pe;
      uint amount;
      uint h;
      uint time;
      uint cmd;
      Cpay[8] cpay;
   }

   struct Input {
      Payment pay;
      uint balance;
      bytes sig;
   }

   struct State {
      uint r;
      mapping(address => Input) inputs;
      uint F;
      bytes sigcus;
      uint valid;
   }

   uint _totalValue;
   uint _total;
   address[] _users;

   mapping(address => State) _userData;

   address[] _DP;
   uint _deadline;
   uint _bestRound;
   State _bestState;


   event EventDeparture();
   event EventClosureH();
   event EventClosureM();
   event EventResolve();

   //验证conpay是否成对

   function check_conpay(address pos,address id1,address id2) public returns(uint) {
      State storage state1 = _userData[pos];
      for(uint i=0;i<state1.inputs[id1].pay.cpay.length;i++) {
         bool flag = false;
         Cpay storage conpay1 = state1.inputs[id1].pay.cpay[i];
         for(uint j=0;j<state1.inputs[id2].pay.cpay.length;j++) {
            Cpay storage conpay2 = state1.inputs[id2].pay.cpay[j];
            if(conpay1.round == conpay2.round && conpay1.pr == conpay2.pr && conpay1.pe == conpay2.pe) {
               flag = true;
               break;
            }
         }
         if(!flag) {
            return 0;
         }
      }
      return 1;
   }
   

   //验证余额更新是否正确
   function check_update(address pos) public returns(uint) {
      State storage state1 = _userData[pos];
      State storage state2 = _bestState;
      for(uint i=0;i<_users.length;i++) {
         address idx = _users[i];
         uint balance1 = state1.inputs[idx].balance;
         uint balance2 = state2.inputs[idx].balance;
         uint change;

         if(state1.inputs[idx].pay.pr == idx) {
            change = -state1.inputs[idx].pay.amount;
         }
         else if(state1.inputs[idx].pay.pe == idx) {
            change = state1.inputs[idx].pay.amount;
         }
         else {
            change = 0;
         }

         if(balance1 + change != balance2) {
            return i+2;
         }
      }

      return 1;
   }


   //验证轮次是否正确
   function check_round(address pos) public returns(uint) {
      State storage state1 = _userData[pos];
      State storage state2 = _bestState;
      for(uint i=0;i<_users.length;i++) {
         address idx = _users[i];
         if(state1.inputs[idx].pay.round != state2.inputs[idx].pay.round && 
         state1.inputs[idx].pay.round <= state2.r) {
            return i+2;
         }
      }
      return 1;
   }

   function state_equal(address pos) public returns(uint) {
      State storage state1 = _userData[pos];
      State storage state2 = _bestState;

      if(state1.r != state2.r || state1.F != state2.F) {
         return 0;
      }
      for(uint i=0;i<_total;i++) {
         if(_users[i] == address(0x0)) {
            continue;
         }
         Input storage input1 = state1.inputs[_users[i]];
         Input storage input2 = state2.inputs[_users[i]];
         if(input1.balance != input2.balance) {
            return 0;
         }
         Payment storage pay1 = input1.pay;
         Payment storage pay2 = input2.pay;
         if(pay1.tx_type != pay2.tx_type || pay1.round != pay2.round ||
         pay1.pr != pay2.pr || pay1.pe != pay2.pe ||
         pay1.amount != pay2.amount || pay1.h != pay2.h ||
         pay1.time != pay2.time || pay1.cmd != pay2.cmd) {
            return 0;
         }
         for(uint j=0;j<8;j++) {
            Cpay storage cpay1 = pay1.cpay[j];
            Cpay storage cpay2 = pay2.cpay[j];
            if(cpay1.tx_type != cpay2.tx_type || cpay1.round != cpay2.round ||
            cpay1.pr != cpay2.pr || cpay1.pe != cpay2.pe ||
            cpay1.amount != cpay2.amount || cpay1.h != cpay2.h || 
            cpay1.time != cpay2.time) {
               return 0;
            }
         }
      }
      return 1;
   }

   function AuditSin(address pos) public returns(uint) {
      uint i;
      uint j;
      uint r;

      r = _userData[pos].r;
      State storage state1 = _userData[pos];
      //验证签名
      for(i=0;i<_total;i++) {
         if(_users[i] == address(0x0)) {
            continue;
         }
         if(verify_input(pos,_users[i]) != 1) {
            return 7;
         }
      }
      
      //验证金额
      uint sum = 0;
      for(i=0;i<_total;i++) {
         address idx = _users[i];
         //余额为负（uint?）
         if(state1.inputs[idx].balance < 0) {
            return 2;
         }
         //计算总金额
         sum += state1.inputs[idx].balance;
         for(j=0;j<state1.inputs[idx].pay.cpay.length;i++) {
            sum += state1.inputs[idx].pay.cpay[j].amount;
         }
      }
      if(sum != _totalValue) {
         return 3;
      }

      //验证cpay是否成对出现
      for(i=0;i<_total;i++) {
         address idx1 = _users[i];
         for(j=0;j<state1.inputs[idx1].pay.cpay.length;j++) {
            address idx2 = state1.inputs[idx1].pay.cpay[j].pr;
            if(idx1 == idx2) {
               idx2 = state1.inputs[idx1].pay.cpay[j].pe;
            }
            if(check_conpay(pos,idx1,idx2) != 1) {
               return 4;
            }
         }
      }

      //验证轮次信息是否正确

      for(i=0;i<_total;i++) {
         address idx1 = _users[i];
         address idx2 = state1.inputs[idx1].pay.pr;
         if(idx1 == idx2) {
            idx2 = state1.inputs[idx1].pay.pe;
         }
         Payment storage pay1 = state1.inputs[idx1].pay;
         Payment storage pay2 = state1.inputs[idx2].pay;
         if(pay1.round > r || pay2.round > r || pay2.round > pay1.round) {
            return 5;
         }
         if(pay1.round == pay2.round) {
            if(pay1.tx_type != pay2.tx_type || pay1.round != pay2.round || 
            pay1.pr != pay2.pr || pay1.pe != pay2.pe || 
            pay1.amount != pay2.amount || pay1.h != pay2.h || 
            pay1.time != pay2.time || pay1.cmd != pay2.cmd) {
               return 6;
            }
            for(uint j=0;j<8;j++) {
               if(pay1.cpay[j].tx_type != pay2.cpay[j].tx_type || pay1.cpay[j].round != pay2.cpay[j].round || 
               pay1.cpay[j].pr != pay2.cpay[j].pr || pay1.cpay[j].pe != pay2.cpay[j].pe || 
               pay1.cpay[j].amount != pay2.cpay[j].amount || pay1.cpay[j].h != pay2.cpay[j].h || 
               pay1.cpay[j].time != pay2.cpay[j].time) {
                  return 7;
               }
            }
         }
      }

      return 1;
   }

   function AuditDou(address pos) public returns(uint) {
      State storage state1 = _userData[pos];
      State storage state2 = _bestState;
      uint r1 = state1.r;
      //Input input1 = state1.input;
      //?sig
      uint F1 = state1.F;

      uint r2 = state2.r;
      //Input input2 = state2.input;
      //?sig
      uint F2 = state2.F;

      if(r1 == r2) {
         if(state_equal(pos) != 1) { //others to be added
            return 2;
         }
      }
      else if(r1 == r2 + 1 && check_update(pos) != 1) {
         return 3;
      }
      if(r1 > r2 + 1 && check_round(pos) != 1) {
         return 4;
      }

      return 1;
   }

   function Audit(address pos) public returns(uint) {
      State memory state1 = _userData[pos];
      State memory state2 = _bestState;

      uint v = verify_state(pos);
      if(v == 1 && state1.valid != 1) {
         state1.valid = 0;
      }
      if(v != 1 && AuditSin(pos) != 1) {
         punish();
         return 2;
      }

      if(state1.valid == 1 && state2.valid == 1 && AuditDou(pos) != 1) {
         punish();
         return 3;
      }
      return 1;
   }

   function hash_conpay(address pos,address id) public returns(bytes32) {
      Payment memory p = _userData[pos].inputs[id].pay;
      Cpay memory c = p.cpay[0];
      bytes memory b;
      bytes32 tmp;

      for(uint i=0;i<8;i++) {
         c = p.cpay[i];
         tmp = keccak256(abi.encodePacked(c.tx_type,c.round,c.pr,c.pe,c.amount,c.h,c.time));
         b = abi.encodePacked(b,tmp);
      }
      bytes32 ans = keccak256(b);
      return ans;
   }

   function hash_input(address pos,address id) public returns(bytes32) {
      Input memory inp = _userData[pos].inputs[id];
      Payment memory p = _userData[pos].inputs[id].pay;
      bytes32 cpay_h = hash_conpay(pos,id);
      bytes32 ans = keccak256(abi.encodePacked(p.tx_type,p.round,p.pr,p.pe,p.amount,p.h,p.time,p.cmd,cpay_h,inp.balance));
      return ans;
   }

   function hash_state(address pos) public returns(bytes32) {
      State memory s = _userData[pos];
      bytes memory b = abi.encodePacked(s.r);
      bytes32 tmp;
      for(uint i=0;i<_total;i++) {
         tmp = hash_input(pos,_users[i]);
         b = abi.encodePacked(b,tmp);
      }
      bytes32 ans = keccak256(abi.encodePacked(b,s.F));
      return ans;
   }

   function recover(bytes32 hash, bytes memory sig) public pure returns (address) {
      bytes32 r;
      bytes32 s;
      uint8 v;

      //Check the signature length
      if (sig.length != 65) {
         return (address(0));
      }

      // Divide the signature in r, s and v variables
      assembly {
         r := mload(add(sig, 32))
         s := mload(add(sig, 64))
         v := byte(0, mload(add(sig, 96)))
      }

      // Version of signature should be 27 or 28, but 0 and 1 are also possible versions
      if (v < 27) {
         v += 27;
      }

      // If the version is correct return the signer address
      if (v != 27 && v != 28) {
         return (address(0));
      } 
      else {
         return ecrecover(hash, v, r, s);
      }
   }

   function verify_input(address pos,address id) public returns(uint) {
      bytes32 h = hash_input(pos,id);
      bytes memory sig = _userData[pos].inputs[id].sig; //sig
      address a = recover(h,sig);
      if(a == id) {
         return 1;
      }
      return 0;
   }

   function verify_state(address pos) public returns(uint) {
      return 1; //debug
      bytes32 h = hash_state(pos);
      bytes memory sig = _userData[pos].sigcus; //sig
      address a = recover(h,sig);
      if(a == _users[0]) {
         return 1;
      }
      return 0;
   }

   function depart(address pos) public {
      if(_DP.length == 0) {
         _deadline = now + 1 minutes;
         _DP.push(pos);
      }
      if(_userData[pos].valid == 1) {
         record(pos);
      }
      emit EventDeparture();
   }

   function record(address pos) public returns(uint) {
      //if(now >= _deadline) {
      //   return;
      //}
      uint r = _userData[pos].r;
      if(Audit(pos) != 1) {
         return 2;
      }
      if(r > _bestRound) {
         _bestRound = r;
         set_beststate(pos);
      }
      return 3;
   }

   function resolve() public {
      //if(!(_DP.length != 0 && now > _deadline)) {
      //   return;
      //}
      //??//updatecon
      bool flag = false;
      uint r = _bestState.r;

      for(uint i=0;i<_DP.length;i++) {
         if(_DP[i] == _users[0]) {
            flag = true;
            break;
         }
      }
      if(flag) { // conpay
         //send
         emit EventClosureH();
      }
      else {
         for(uint i=0;i<_DP.length;i++) {
            if(true) {
               //send
               for(uint j=0;j<_total;j++) {
                  if(_users[j] == _DP[i]) {
                     _users[j] = address(0x0);
                     break;
                  }
               }
               _totalValue -= _bestState.inputs[_DP[i]].balance;
            }
         }
         _bestState.r = _bestState.r + 1;
         _bestRound = _bestState.r;
         delete _DP;
         emit EventResolve();
      }
   }

   function punish() public returns(uint) {
      uint dbs = (_totalValue) / (_total - 1); // +G?
      for(uint i=1;i<_total;i++) {
         //_users[i].call.value(dbs * 1 ether);
      }
      emit EventClosureM();
   }

   constructor() public{
      _total = 0;
      _totalValue = 1000;
   }

   function add_user(address id) public {
      _users.push(id);
      _total += 1;
   }

   function set_beststate(address pos) public {
      
      State storage state1 = _userData[pos];
      _bestState.r = state1.r;
      _bestState.F = state1.F;
      _bestState.sigcus = state1.sigcus;
      _bestState.valid = state1.valid;
      for(uint i=0;i<_total;i++) {
         address idx = _users[i];
         _bestState.inputs[idx].balance = state1.inputs[idx].balance;
         _bestState.inputs[idx].sig = state1.inputs[idx].sig;

         _bestState.inputs[idx].pay.tx_type = state1.inputs[idx].pay.tx_type;
         _bestState.inputs[idx].pay.round = state1.inputs[idx].pay.round;
         _bestState.inputs[idx].pay.pr = state1.inputs[idx].pay.pr;
         _bestState.inputs[idx].pay.pe = state1.inputs[idx].pay.pe;
         _bestState.inputs[idx].pay.amount = state1.inputs[idx].pay.amount;
         _bestState.inputs[idx].pay.h = state1.inputs[idx].pay.h;
         _bestState.inputs[idx].pay.time = state1.inputs[idx].pay.time;
         _bestState.inputs[idx].pay.cmd = state1.inputs[idx].pay.cmd;

         for(uint j=0;j<8;j++) {
            /*
            _bestState.inputs[idx].pay.cpay[j].tx_type = state1.inputs[idx].pay.cpay[j].tx_type;
            _bestState.inputs[idx].pay.cpay[j].round = state1.inputs[idx].pay.cpay[j].round;
            _bestState.inputs[idx].pay.cpay[j].pr = state1.inputs[idx].pay.cpay[j].pr;
            _bestState.inputs[idx].pay.cpay[j].pe = state1.inputs[idx].pay.cpay[j].pe;
            _bestState.inputs[idx].pay.cpay[j].amount = state1.inputs[idx].pay.cpay[j].amount;
            _bestState.inputs[idx].pay.cpay[j].h = state1.inputs[idx].pay.cpay[j].h;
            _bestState.inputs[idx].pay.cpay[j].time = state1.inputs[idx].pay.cpay[j].time;
            */
         }
         
      }
      
   }

   function set_input(address pos,address id,uint tx_type,uint round,address pr,address pe,uint amount,uint h,uint time,
   uint cmd,uint balance) public {
      _userData[pos].inputs[id].pay.tx_type = tx_type;
      _userData[pos].inputs[id].pay.round = round;
      _userData[pos].inputs[id].pay.pr = pr;
      _userData[pos].inputs[id].pay.pe = pe;
      _userData[pos].inputs[id].pay.amount = amount;
      _userData[pos].inputs[id].pay.h = h;
      _userData[pos].inputs[id].pay.time = time;
      _userData[pos].inputs[id].pay.cmd = cmd;
      _userData[pos].inputs[id].balance = balance;
   }

   function set_input_sig(address pos,address id,bytes memory sig) public {
      _userData[pos].inputs[id].sig = sig;
   }

   function get_input_sig(address pos,address id) public returns(bytes memory) {
      return _userData[pos].inputs[id].sig;
   }

   function set_state_sig(address pos,bytes memory sig) public {
      _userData[pos].sigcus = sig;
   }

   function get_state_sig(address pos) public returns(bytes memory) {
      return _userData[pos].sigcus;
   }

   function add_conpay(address pos,address id,uint tx_type,uint round,address pr,address pe,uint amount,uint h,uint time) public {
      uint i;
      for(i=0;i<_userData[pos].inputs[id].pay.cpay.length;i++) {
         if(_userData[pos].inputs[id].pay.cpay[i].tx_type != 10) {
            break;
         }
      }
      
      if(i < _userData[pos].inputs[id].pay.cpay.length) {
         //Cpay memory c = _state[_state.length-1].inputs[id].pay.cpay[i];
         _userData[pos].inputs[id].pay.cpay[i].tx_type = tx_type;
         _userData[pos].inputs[id].pay.cpay[i].round = round;
         _userData[pos].inputs[id].pay.cpay[i].pr = pr;
         _userData[pos].inputs[id].pay.cpay[i].pe = pe;
         _userData[pos].inputs[id].pay.cpay[i].amount = amount;
         _userData[pos].inputs[id].pay.cpay[i].h = h;
         _userData[pos].inputs[id].pay.cpay[i].time = time;
      }
   }

   function get_data(address pos,address id) public returns(uint) {
      return _userData[pos].inputs[id].pay.tx_type;
   }

   function get_data2(address pos,address id) public returns(uint) {
      return _userData[pos].inputs[id].pay.cpay[0].tx_type + _userData[pos].inputs[id].pay.cpay[1].tx_type;
   }

   function get_data3() public returns(uint) {
      return _totalValue + _bestState.r;
   }

/*
   function getResult() public view returns(uint){
      uint a = 1;
      uint b = 2;
      uint result = a + b;
      //uint[5] memory z = [uint(4),3,5,1,2];
      //z.sort();
      
      //return z[4];
   }
*/
}