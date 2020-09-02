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

   uint16[] _DP;
   uint _deadline;
   uint32 _bestRound;
   State _bestState;


   event EventDeparture();
   event EventClosureH();
   event EventClosureM();
   event EventResolve();

   function zAudit(bytes memory data) public returns(uint) {
      uint n = _total;

      bytes memory sig = new bytes(65);
      bytes memory zinput = new bytes(20);
      uint sum;
      uint r;

      uint ans = 15;
      for(uint i=0;i<4;i++) {
         r = r << 8;
         r += uint8(data[n * 85 + i]);
      }

      for(uint j=0;j<n;j++) {
         uint all = 0;
         for(uint i=0;i<20;i++) {
            uint tmp = uint8(data[j * 85 + i]);
            all = all << 8;
            all += tmp;
         }
         for(uint i=0;i<65;i++) {
            sig[i] = data[j * 85 + 20 + i];
         }
         for(uint i=0;i<20;i++) {
            zinput[i] = data[j * 85 + i];
         }

         if(ans & 1 == 1) {
            bytes32 input_hash = keccak256(zinput);
            address input_addr = recover(input_hash,sig);
            if(input_addr != _users[j]) {
               ans &= 14;
            }
         }

         sum += (all & ((1 << 48) - 1));
/*
struct Payment {
      uint32 round; 128    ((all & (((1 << 32) - 1) << 128)) >> 128)
      uint16 pr; 112       ((all & (((1 << 16) - 1) << 112)) >> 112)
      uint16 pe; 96        ((all & (((1 << 16) - 1) << 96)) >> 96)
      uint48 amount; 48    ((all & (((1 << 48) - 1) << 48)) >> 48)
   }

   struct Input {
      Payment pay;
      uint48 balance; 0    (all & ((1 << 48) - 1))
      bytes sig;
   }
   */
         if(((all & (((1 << 32) - 1) << 112)) >> 112) != 65535) {
            uint idx;
            uint round2;
            uint pr2;
            uint pe2;
            uint amount2;

            if(((all & (((1 << 16) - 1) << 112)) >> 112) != j) {
               idx = ((all & (((1 << 16) - 1) << 112)) >> 112);
            }
            else {
               idx = ((all & (((1 << 16) - 1) << 96)) >> 96);
            }

            round2 = 0;
            for(uint i=0;i<4;i++) {
               round2 = round2 << 8;
               round2 += uint8(data[idx * 85 + i]);
            }

            pr2 = 0;
            for(uint i=4;i<6;i++) {
               pr2 = pr2 << 8;
               pr2 += uint8(data[idx * 85 + i]);
            }

            pe2 = 0;
            for(uint i=6;i<8;i++) {
               pe2 = pe2 << 8;
               pe2 += uint8(data[idx * 85 + i]);
            }

            amount2 = 0;
            for(uint i=8;i<14;i++) {
               amount2 = amount2 << 8;
               amount2 += uint8(data[idx * 85 + i]);
            }

            if(((all & (((1 << 32) - 1) << 128)) >> 128) > r || round2 > r
                  || ((all & (((1 << 32) - 1) << 128)) >> 128) > round2) {
               ans &= 11;
            }
            if(((all & (((1 << 32) - 1) << 128)) >> 128) != round2 
                  || ((all & (((1 << 16) - 1) << 112)) >> 112) != pr2 
                  || ((all & (((1 << 16) - 1) << 96)) >> 96) != pe2 
                  || ((all & (((1 << 48) - 1) << 48)) >> 48) != amount2) {
               ans &= 11;
            }
         }

         uint r_b = _bestState.r;
         uint len = _total;
         if(r > r_b + 1) {
            uint round = ((all & (((1 << 32) - 1) << 128)) >> 128);
            uint pr = ((all & (((1 << 16) - 1) << 112)) >> 112);
            uint pe = ((all & (((1 << 16) - 1) << 96)) >> 96);
            uint amount = ((all & (((1 << 48) - 1) << 48)) >> 48);
            uint balance = (all & ((1 << 48) - 1));

            address idx = _users[j];
            if(_bestState.inputs[idx].pay.round != round && 
                  _bestState.inputs[idx].pay.round <= r) {
               ans &= 7;
            }
         }
         else if(r == r_b + 1) {
            address idx = _users[j];
            uint balance1 = _bestState.inputs[idx].balance;
            uint balance2 = (all & ((1 << 48) - 1));
            uint b;

            if(_bestState.inputs[idx].pay.pr == j) {
               b = balance1 - _bestState.inputs[idx].pay.amount;
            }
            else if(_bestState.inputs[idx].pay.pe == j) {
               b = balance1 + _bestState.inputs[idx].pay.amount;
            }
            else {
               b = balance1;
            }

            if(b != balance2) {
               ans &= 7;
            }
         }
         else {
            ans &= 7;
         }
         
      }
      
      bytes memory tmp = new bytes(n * 85 + 10);
      for(uint i=0;i<n * 85 + 10;i++) {
         tmp[i] = data[i];
      }
      bytes32 state_hash = keccak256(tmp);
      bytes memory state_sig = new bytes(65);
      for(uint i=0;i<65;i++) {
         state_sig[i] = data[n*85+10+i];
      }
      address state_addr = recover(state_hash,state_sig);
      if(state_addr != _users[0]) {
         ans &= 13;
      }
      
      
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

   function depart(uint16 pos) public {
      /*
      if(_DP.length == 0) {
         _deadline = now + 1 minutes;
         _DP.push(pos);
      }
      if(_userData[_users[pos]].valid) {
         record(pos);
      }
      emit EventDeparture();
      */
   }

   function record(uint16 pos) public returns(uint) {
      //if(now >= _deadline) {
      //   return;
      //}
      /*
      uint32 r = _userData[_users[pos]].r;
      if(Audit(pos) != 1) {
         return 2;
      }
      if(r > _bestRound) {
         _bestRound = r;
         set_beststate(pos);
      }
      return 3;
      */
   }

   function resolve() public {
      //if(!(_DP.length != 0 && now > _deadline)) {
      //   return;
      //}

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

   function add_user(bytes memory data) public {
      uint len = data.length;
      bytes memory tmp = new bytes(20);
      address id;
      uint16 n = _total;
      for(uint i=0;i<len;i+=20) {
         for(uint j=0;j<20;j++) {
            tmp[j] = data[i+j];
         }
         assembly {
            id := mload(add(tmp,20))
         }
         _users.push(id);
         n += 1;
      }
      _total = n;
   }

   function set_beststate(bytes memory data) public returns(uint16) {
      uint n = _total;

      for(uint j=0;j<n;j++) {
         uint all = 0;
         address idx = _users[j];
         for(uint i=0;i<20;i++) {
            uint tmp = uint8(data[j * 85 + i]);
            all = all << 8;
            all += tmp;
         }
         
         _bestState.inputs[idx].pay.round = uint32((all & (((1 << 32) - 1) << 128)) >> 128);
         _bestState.inputs[idx].pay.pr = uint16((all & (((1 << 16) - 1) << 112)) >> 112);
         _bestState.inputs[idx].pay.pe = uint16((all & (((1 << 16) - 1) << 96)) >> 96);
         _bestState.inputs[idx].pay.amount = uint48((all & (((1 << 48) - 1) << 48)) >> 48);
         _bestState.inputs[idx].balance = uint48(all & ((1 << 48) - 1));
      }

      uint r=0;
      uint F=0;
      for(uint i=0;i<4;i++) {
         r = r << 8;
         r += uint8(data[n * 85 + i]);
      }
      for(uint i=0;i<6;i++) {
         F = F << 8;
         F += uint8(data[n * 85 + 4 + i]);
      }
      _bestState.r = uint32(r);
      _bestState.F = uint48(F);

      return _total;
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