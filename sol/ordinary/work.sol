pragma solidity ^0.6.0;

contract work {

   struct Payment {
      uint32 round;
      uint16 pr;
      uint16 pe;
      uint48 amount;
   }

   struct Input {
      Payment pay;
      uint48 balance;
      bytes sig;
   }

   struct State {
      uint32 r;
      mapping(address => Input) inputs;
      uint48 F;
      bytes sigcus;
      bool valid;
   }

   uint48 _totalValue;
   uint16 _total;
   address[] _users;

   mapping(address => State) _userData;

   uint16[] _DP;
   uint _deadline;
   uint32 _bestRound;
   State _bestState;


   event EventDeparture();
   event EventClosureH();
   event EventClosureM();
   event EventResolve();

   //验证余额更新是否正确
   function check_update(uint16 pos) public returns(uint) {
      State storage state1 = _bestState;
      State storage state2 = _userData[_users[pos]];
      for(uint16 i=0;i<_users.length;i++) {
         address idx = _users[i];
         uint48 balance1 = state1.inputs[idx].balance;
         uint48 balance2 = state2.inputs[idx].balance;
         uint48 b;

         if(state1.inputs[idx].pay.pr == i) {
            b = balance1 - state1.inputs[idx].pay.amount;
         }
         else if(state1.inputs[idx].pay.pe == i) {
            b = balance1 + state1.inputs[idx].pay.amount;
         }
         else {
            b = balance1;
         }

         if(b != balance2) {
            return i+2;
         }
      }

      return 1;
   }


   //验证轮次是否正确
   function check_round(uint16 pos) public returns(uint) {
      State storage state1 = _bestState;
      State storage state2 = _userData[_users[pos]];
      for(uint16 i=0;i<_users.length;i++) {
         address idx = _users[i];
         if(state1.inputs[idx].pay.round != state2.inputs[idx].pay.round && 
         state1.inputs[idx].pay.round <= state2.r) {
            return i+2;
         }
      }
      return 1;
   }

   function state_equal(uint16 pos) public returns(uint) {
      State storage state1 = _bestState;
      State storage state2 = _userData[_users[pos]];

      if(state1.r != state2.r || state1.F != state2.F) {
         return 0;
      }
      for(uint16 i=0;i<_total;i++) {
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
         if(pay1.round != pay2.round || pay1.pr != pay2.pr || 
         pay1.pe != pay2.pe || pay1.amount != pay2.amount) {
            return 0;
         }
      }
      return 1;
   }

   function AuditSin(uint16 pos) public returns(uint) {
      uint16 i;
      uint32 r;

      r = _userData[_users[pos]].r;
      State storage state1 = _userData[_users[pos]];
      
      //验证金额
      uint48 sum = 0;
      for(i=0;i<_total;i++) {
         address idx = _users[i];
         //余额为负（uint?）
         if(false) {  //state1.inputs[idx].balance < 0
            return 2;
         }
         //计算总金额
         sum += state1.inputs[idx].balance;
      }
      if(sum != _totalValue) {
         return 3;
      }

      //验证轮次信息是否正确
      for(i=0;i<_total;i++) {
         address idx1 = _users[i];
         if(state1.inputs[idx1].pay.pr == 65535) {
            continue;
         }
         address idx2 = _users[state1.inputs[idx1].pay.pr];
         if(idx1 == idx2) {
            idx2 = _users[state1.inputs[idx1].pay.pe];
         }
         Payment storage pay1 = state1.inputs[idx1].pay;
         Payment storage pay2 = state1.inputs[idx2].pay;
         if(pay1.round > r || pay2.round > r || pay2.round > pay1.round) {
            return 5;
         }
         if(pay1.round == pay2.round) {
            if(pay1.round != pay2.round || pay1.pr != pay2.pr || 
            pay1.pe != pay2.pe || pay1.amount != pay2.amount) {
               return 6;
            }
         }
      }

      return 1;
   }

   function AuditDou(uint16 pos) public returns(uint) {
      State storage state1 = _userData[_users[pos]];
      State storage state2 = _bestState;
      uint32 r1 = state1.r;
      uint48 F1 = state1.F;
      uint32 r2 = state2.r;
      uint48 F2 = state2.F;

      if(r1 < r2) {
         return 5;
      }
      else if(r1 == r2) {
         if(state_equal(pos) != 1) {
            return 2;
         }
      }
      else if(r1 == r2 + 1) {
         if(check_update(pos) != 1) {
            return 3;
         } 
      }
      else if(r1 > r2 + 1) {
         if(check_round(pos) != 1) {
            return 4;
         }
      }

      return 1;
   }

   function Audit(uint16 pos) public returns(uint) {
      State memory state1 = _userData[_users[pos]];
      State memory state2 = _bestState;

      uint v = verify_sgn(pos);
      bool sig_i;
      bool sig_s;
      if(v & 1 == 1) {
         sig_i = true;
      }
      else {
         sig_i = false;
      }
      if(v & 2 == 2) {
         sig_s = true;
      }
      else {
         sig_s = false;
      }
      bool v_i = (sig_i && AuditSin(pos) == 1);
      bool v_s = (AuditDou(pos) == 1);

      if(!sig_s && state_equal(pos) != 1) {
         state1.valid = false;
      }
      if(sig_s && !v_i) {
         punish();
         return 2;
      }

      if(state1.valid && state2.valid && !v_s) {
         punish();
         return 3;
      }
      return 1;
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

   function verify_sgn(uint16 pos) public returns(uint) {
      State memory s = _userData[_users[pos]];
      bytes memory state_tmp = abi.encodePacked(s.r);
      bytes32 state_hash;
      uint ans = 3;

      for(uint16 i=0;i<_total;i++) {
         Input memory inp = _userData[_users[pos]].inputs[_users[i]];
         Payment memory p = _userData[_users[pos]].inputs[_users[i]].pay;
         bytes32 input_hash = keccak256(abi.encodePacked(p.round,p.pr,p.pe,p.amount,inp.balance));

         bytes memory input_sig = _userData[_users[pos]].inputs[_users[i]].sig;
         address input_addr = recover(input_hash,input_sig);
         if(input_addr != _users[i]) {
            ans = 2;
         }
         state_tmp = abi.encodePacked(state_tmp,input_hash);
      }

      state_tmp = abi.encodePacked(state_tmp,s.F);
      state_hash = keccak256(state_tmp);
      bytes memory state_sig = _userData[_users[pos]].sigcus;
      address state_addr = recover(state_hash,state_sig);
      if(state_addr != _users[0]) {
         ans -= 2;
      }

      return ans;
   }

   function depart(uint16 pos) public {
      if(_DP.length == 0) {
         _deadline = now + 1 minutes;
         _DP.push(pos);
      }
      if(_userData[_users[pos]].valid) {
         record(pos);
      }
      emit EventDeparture();
   }

   function record(uint16 pos) public returns(uint) {
      //if(now >= _deadline) {
      //   return;
      //}
      uint32 r = _userData[_users[pos]].r;
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
      uint32 r = _bestState.r;

      for(uint16 i=0;i<_DP.length;i++) {
         if(_DP[i] == 0) {
            flag = true;
            break;
         }
      }
      if(flag) { // conpay
         //send
         emit EventClosureH();
      }
      else {
         for(uint16 i=0;i<_DP.length;i++) {
            //send
            _users[i] = address(0x0);
            _totalValue -= _bestState.inputs[_users[_DP[i]]].balance;
         }
         _bestState.r = _bestState.r + 1;
         _bestRound = _bestState.r;
         _total -= uint16(_DP.length);
         delete _DP;
         emit EventResolve();

         uint16 Index = 0;
         for(uint16 i=0;i<_users.length;i++) {
            if(_users[i] != address(0x0)) {
               _users[Index] = _users[i];
               Index++;
            }
         }
         for(uint16 i=Index;i<_users.length;i++) {
            delete _users[i];
         }
      }
   }

   function punish() public returns(uint) {
      uint48 dbs = (_totalValue) / (_total - 1); // +G?
      for(uint16 i=1;i<_total;i++) {
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

   function set_beststate(uint16 pos) public returns(uint16) {
      State storage state1 = _userData[_users[pos]];
      _bestState.r = state1.r;
      _bestState.F = state1.F;
      _bestState.sigcus = state1.sigcus;
      _bestState.valid = state1.valid;
      for(uint16 i=0;i<_total;i++) {
         address idx = _users[i];
         _bestState.inputs[idx].balance = state1.inputs[idx].balance;
         _bestState.inputs[idx].sig = state1.inputs[idx].sig;

         _bestState.inputs[idx].pay.round = state1.inputs[idx].pay.round;
         _bestState.inputs[idx].pay.pr = state1.inputs[idx].pay.pr;
         _bestState.inputs[idx].pay.pe = state1.inputs[idx].pay.pe;
         _bestState.inputs[idx].pay.amount = state1.inputs[idx].pay.amount;
      }
      return _total;
   }

   function set_input(uint16 pos,uint16 id,uint32 round,uint16 pr,uint16 pe,uint48 amount,uint48 balance) public {
      _userData[_users[pos]].inputs[_users[id]].pay.round = round;
      _userData[_users[pos]].inputs[_users[id]].pay.pr = pr;
      _userData[_users[pos]].inputs[_users[id]].pay.pe = pe;
      _userData[_users[pos]].inputs[_users[id]].pay.amount = amount;
      _userData[_users[pos]].inputs[_users[id]].balance = balance;
   }

   function set_input_b(uint16 pos,uint16 id,uint32 round,uint16 pr,uint16 pe,uint48 amount,uint48 balance) public {
      _bestState.inputs[_users[id]].pay.round = round;
      _bestState.inputs[_users[id]].pay.pr = pr;
      _bestState.inputs[_users[id]].pay.pe = pe;
      _bestState.inputs[_users[id]].pay.amount = amount;
      _bestState.inputs[_users[id]].balance = balance;
   }

   function set_round_F(uint16 pos,uint32 r,uint48 F) public {
      _userData[_users[pos]].r = r;
      _userData[_users[pos]].F = F;
   }

   function set_input_sig(uint16 pos,uint16 id,bytes memory sig) public {
      _userData[_users[pos]].inputs[_users[id]].sig = sig;
   }

   function set_input_sig_b(uint16 pos,uint16 id,bytes memory sig) public {
      _bestState.inputs[_users[id]].sig = sig;
   }

   function get_input_sig(uint16 pos,uint16 id) public returns(bytes memory) {
      return _userData[_users[pos]].inputs[_users[id]].sig;
   }

   function set_state_sig(uint16 pos,bytes memory sig) public {
      _userData[_users[pos]].sigcus = sig;
      _userData[_users[pos]].valid = true;
   }

   function get_state_sig(uint16 pos) public returns(bytes memory) {
      return _userData[_users[pos]].sigcus;
   }

   function get_data3() public returns(uint) {
      return _totalValue + _bestState.r;
   }

   function empty() public {
      
   }

   function r(bytes memory zin) public returns(bytes memory) {
      _bestState.F = 5;
      bytes memory aa;
      for(uint16 i=0;i<8;i++) {
         _bestState.inputs[address(0x0)].sig[i] = zin[i+8];
      }
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