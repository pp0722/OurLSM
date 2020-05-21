#!/bin/bash

# This file contains the testing case of our LSM implementation using Oracle.
# We first initialize all the users balance according to the chosen test case. Below the balances are initialized by generating blocks on the Oracle Node and sending coins from there.# Then we send from the transactions of our test case from each wallet to the Oracle using the new bitcoin API calls -sendtoaddressLSM which will redirect unfunded transaction to the Oracle node. Therefore to use this script, it is required to start the Oracle Node first using oracleServer.py .
# Once the Oracle received the transaction, the latter will periodically start gridlock sessions and send the solution to the network which will eventually update the wallet balance of users involved in the gridlock sessions.


# Helping functions
showTime() {
        startTimestamp=$(date +"%s")
        startTime=$(date)
	echo "[INFO] $startTimestamp - $startTime"
}

# Wallet balance initialization

# Simple Case : two users test case. A initial balance 100. B initial balance : 50
# A sends 150 to B. B sends 100 to A. 
balanceArr=(100 50)

# Ubin test Case (See Ubin Phase 2 pdf file)
#ubinBalanceArr=(3 4 5 4 3)


echo "[INFO] init balance ..."

echo "[INFO] generate new address for wallet A"
addressA=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
echo "[INFO]send ${balanceArr[0]} to wallet A"
bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressA ${balanceArr[0]}

echo "[INFO] generate new address for wallet B"
addressB=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf getnewaddress)
echo "[INFO] send ${balanceArr[1]} to wallet B"
bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressB ${balanceArr[1]}




echo "[INFO] generate new block to update the balance"
sleep 1
bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf generate 1

# Send transaction to Oracle

echo "\n[INFO] send transactions to Oracle"

echo "[INFO] A sends 150 to B"
bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddressLSM $addressB 150

sleep 0.5
echo "[INFO] B sends 100 to A"
bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf sendtoaddressLSM $addressA 100



