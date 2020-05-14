#!/bin/bash

bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf generate 101

# Init user A
userA=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
#bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddress $userA 3

# Init user B
userB=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
#bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddress $userB 4

# Init user C
userC=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
#bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddress $userC 5

# Init user D
userD=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
#bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddress $userD 4

# Init user E
userE=$(bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf getnewaddress)
#bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendtoaddress $userE 3

# Send money to user in one transaction only
bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf sendmany "" "{\"$userA\": 3,\"$userB\" : 4, \"$userC\" : 5, \"$userD\" : 4, \"$userE\" : 5}"


# Generate 1 block to initialize all the starting balance
#bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf generate 1







