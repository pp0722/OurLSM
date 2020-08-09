#!/bin/bash

# This file contains the testing case of our LSM implementation using Oracle.
# We first initialize all the users balance according to the chosen test case. Below the balances are initialized by generating blocks on the Oracle Node and sending coins from there.
# Then we send from the transactions of our test case from each wallet to the Oracle using the new bitcoin API calls -sendtoaddressLSM which will redirect unfunded transaction to the Oracle node. 
# Therefore to use this script, it is required to start the Oracle Node first using oracleContract.py .
# Once the Oracle received the transaction, the latter will periodically start gridlock sessions and send the solution to the network which will eventually update the wallet balance of users involved in the gridlock sessions.


# Helping functions
showTime() {
        startTimestamp=$(date +"%s")
        startTime=$(date)
	echo "[INFO] $startTimestamp - $startTime"
}
 


if [ -z $1 ] || [ $1 == "bilateral"]
then 
        # Simple Case : two users test case. A initial balance 100. B initial balance : 50
        # A sends 150 to B. 
        # B sends 100 to A.

        echo "[INFO] Test case set to BILATERAL"
        balanceArr=(100 50)

        echo "[INFO] init users' wallet balance ..."

        echo "[INFO] generate new address for wallet A"
        addressA=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
        echo "[INFO]Oracle send ${balanceArr[0]} to wallet A"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressA ${balanceArr[0]}

        echo "[INFO] generate new address for wallet B"
        addressB=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf getnewaddress)
        echo "[INFO] Oracle send ${balanceArr[1]} to wallet B"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressB ${balanceArr[1]}


        echo "[INFO] generate new block to update the balance"
        sleep 1
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf generate 1

        # Send LSM transaction to Oracle

        echo "\n[INFO] send transactions to Oracle"

        echo "[INFO] A sends 150 to B"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddressLSM $addressB 150

        sleep 0.5
        echo "[INFO] B sends 100 to A"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf sendtoaddressLSM $addressA 100

elif [ $1 == "ubin" ]
then 
        # Ubin test Case (See Ubin Phase 2 PDF report  )
        # 5 users and 10 transactions
        echo "[INFO] Test case set to UBIN"
        balanceArr=(3 4 5 4 3)


        echo "[INFO] init users' wallet balance ..."

        echo "[INFO] generate new address for wallet A"
        addressA=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
        echo "[INFO]Oracle send ${balanceArr[0]} to wallet A"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressA ${balanceArr[0]}

        echo "[INFO] generate new address for wallet B"
        addressB=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf getnewaddress)
        echo "[INFO] Oracle send ${balanceArr[1]} to wallet B"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressB ${balanceArr[1]}

        echo "[INFO] generate new address for wallet C"
        addressC=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoinC/ -conf=/home/david/.bitcoinC/bitcoin.conf getnewaddress)
        echo "[INFO] Oracle send ${balanceArr[2]} to wallet C"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressC ${balanceArr[2]}

        echo "[INFO] generate new address for wallet D"
        addressD=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoinD/ -conf=/home/david/.bitcoinD/bitcoin.conf getnewaddress)
        echo "[INFO] Oracle send ${balanceArr[3]} to wallet D"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressD ${balanceArr[3]}


        echo "[INFO] generate new address for wallet E"
        addressE=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoinE/ -conf=/home/david/.bitcoinE/bitcoin.conf getnewaddress)
        echo "[INFO] Oracle send ${balanceArr[4]} to wallet E"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf sendtoaddress $addressE ${balanceArr[4]}

        echo "[INFO] generate new block to update the balance"
        sleep 1
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf generate 1

        # Send LSM transaction to Oracle

        echo "\n[INFO] send transactions to Oracle"

        echo "[INFO] A sends 5 to B"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddressLSM $addressB 5

        sleep 0.2
        echo "[INFO] B sends 6 to C"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf sendtoaddressLSM $addressC 6

        sleep 0.2
        echo "[INFO] B sends 30 to C"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf sendtoaddressLSM $addressC 30

        sleep 0.2
        echo "[INFO] C sends 8 to D"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinC/ -conf=/home/david/.bitcoinC/bitcoin.conf sendtoaddressLSM $addressD 8

        sleep 0.2
        echo "[INFO] C sends 80 to E"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinC/ -conf=/home/david/.bitcoinC/bitcoin.conf sendtoaddressLSM $addressE 80

        sleep 0.2
        echo "[INFO] D sends 7 to E"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinD/ -conf=/home/david/.bitcoinD/bitcoin.conf sendtoaddressLSM $addressE 7

        sleep 0.2
        echo "[INFO] A sends 6 to C"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddressLSM $addressC 6

        sleep 0.2
        echo "[INFO] E sends 8 to A"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinE/ -conf=/home/david/.bitcoinE/bitcoin.conf sendtoaddressLSM $addressA 8

        sleep 0.2
        echo "[INFO] E sends 100 to B"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinE/ -conf=/home/david/.bitcoinE/bitcoin.conf sendtoaddressLSM $addressB 100

        sleep 0.2
        echo "[INFO] D sends 5 to A"
        bitcoin-cli -regtest -datadir=/home/david/.bitcoinD/ -conf=/home/david/.bitcoinD/bitcoin.conf sendtoaddressLSM $addressA 5

elif [ $1 == "random" ]
then 
        echo "[INFO] Test case set to RANDOM (not implemented)"

else
        echo "[ERROR] Wrong test case."
fi
