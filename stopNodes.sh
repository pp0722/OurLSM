#!/bin/bash
#lsof -i -P -n | grep bitcoin


# connect to Oracle on port 8080
bitcoin-cli -regtest -datadir=/home/david/.bitcoin/ -conf=/home/david/.bitcoin/bitcoin.conf stop

bitcoin-cli -regtest -datadir=/home/david/.bitcoinOracle/ -conf=/home/david/.bitcoinOracle/bitcoin.conf stop

