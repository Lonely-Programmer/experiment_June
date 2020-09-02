pragma solidity ^0.6.0;

contract Sign{
    struct zy {
        uint a;
        uint b;
        uint c;
    }

    zy[] public _dat;
    constructor() public{
        
    }

    function add(uint a,uint b,uint c) public returns (uint) {
        _dat.push(zy({a:a,b:b,c:c}));
        return _dat[_dat.length-1].a;
    }

    function look() public returns (uint) {
        return _dat[_dat.length-1].a;
    }

    //uint public _count=7;
    string public _zstr;
    bytes32 public _zhash;
    bytes public _zsig;

    function trial(string memory s,bytes32 hash, bytes memory sig) public {
        _zstr = s;
        _zhash = hash;
        _zsig = sig;
    }
    /**
    * @dev Recover signer address from a message by using his signature
    * @param hash bytes32 message, the hash is the signed message. What is recovered is the signer address.
    * @param sig bytes signature, the signature is generated using web3.eth.sign()
    */
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


    function toBytes(uint x) public returns (bytes32) {
        bytes32 b;
        assembly { mstore(add(b, 32), x) }
        return b;
    }

    function check_hash(string memory mystring, bytes32 expected_result_hash) public returns (bytes32) {
        uint a = 1;
        uint b = 2;
        bytes32 result_hash1 = keccak256(abi.encodePacked(a,b));
        bytes32 result_hash = keccak256(bytes(mystring));
        return result_hash;
    }

    function verify(bytes32 hash, bytes memory sig) public {
        
    }
}