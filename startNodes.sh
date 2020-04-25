#!/bin/bash
#lsof -i -P -n | grep bitcoin


# connect to Oracle on port 8080
# 8333 -> 8080 todo check if Oracle does not run bitcoin protocol wh
bitcoind -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf -txindex -reixndex -addnode=127.0.0.1:8080 -port=8333 -daemon


bitcoind -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf -txindex -port=8335 -addnode=127.0.0.1:8333 -daemon
