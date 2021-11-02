//SPDX-License-Identifier: Unlicense
pragma solidity ^0.7.0;

interface DecimalWrapper {
  event Deposit(address indexed dst, uint wad);
  event Withdrawal(address indexed src, uint wad);

  function deposit(uint256 _amount) external;
  function withdraw(uint256 _amount) external;
}