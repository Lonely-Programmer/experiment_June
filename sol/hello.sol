pragma solidity ^0.6.0;

contract Hello{
  uint public _count=7;

  constructor() public{

  }

  function add(uint a, uint b) public returns(uint){
    _count = _count + 1;
    return a + b + _count - 7;
  }

  function getCount() public returns (uint){
    return _count;
  }

  function say() public returns (string memory) {
    _count = _count + 1;
    return "Hello World!";
  }
}