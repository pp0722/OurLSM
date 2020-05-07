#!/bin/bash
#lsof -i -P -n | grep bitcoin


# Start user nodes and  connect to Oracle on port 8080 to propagate LSM transaction

bitcoind -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf -txindex -reixndex -addnode=127.0.0.1:8080 -port=8333 -daemon
bitcoind -regtest -datadir=/home/david/.bitcoinB/ -conf=/home/david/.bitcoinB/bitcoin.conf -txindex -reixndex -addnode=127.0.0.1:8080 -port=8331 -daemon
#bitcoind -regtest -datadir=/home/david/.bitcoinC/ -conf=/home/david/.bitcoinC/bitcoin.conf -txindex -reixndex -addnode=127.0.0.1:8080 -port=8329 -daemon
#bitcoind -regtest -datadir=/home/david/.bitcoinD/ -conf=/home/david/.bitcoinD/bitcoin.conf -txindex -reixndex -addnode=127.0.0.1:8080 -port=8327 -daemon
#bitcoind -regtest -datadir=/home/david/.bitcoinE/ -conf=/home/david/.bitcoinE/bitcoin.conf -txindex -reixndex -addnode=127.0.0.1:8080 -port=8325 -daemon


# Oracle need to be connected to only one node with the Bitcoin protocol
# It is possible to connect the Oracle to only one user node with the bitcoin protocol if all other nodes are connect between themselves.

# Oracle addnode in bitcoin.conf
bitcoind -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf -txindex -port=8335 -daemon
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8331" "add"
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8329" "add"
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8327" "add"
#bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf addnode "127.0.0.1:8325" "add"

sleep 1

# Oracle generate initial blocks to initialize users balance afterwards
bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf generate 105
