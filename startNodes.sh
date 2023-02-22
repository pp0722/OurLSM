#!/bin/bash
#lsof -i -P -n | grep bitcoin


# Start user nodes and  connect to Oracle on port 8080 to propagate LSM transaction

bitcoind -datadir=./test/lsm/A/
bitcoind -datadir=./test/lsm/B/
bitcoind -datadir=./test/lsm/C/
bitcoind -datadir=./test/lsm/D/
bitcoind -datadir=./test/lsm/E/


# Oracle need to be connected to only one node with the Bitcoin protocol
# It is possible to connect the Oracle to only one user node with the bitcoin protocol if all other nodes are connect between themselves.

# Oracle addnode in bitcoin.conf
bitcoind -datadir=./test/lsm/O/
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8331" "add"
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8329" "add"
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8327" "add"
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8325" "add"

sleep 3

# Oracle generate initial blocks to initialize users balance afterwards
bitcoin-cli -datadir=./test/lsm/O/ generate 110
