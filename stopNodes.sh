#!/bin/bash
#lsof -i -P -n | grep bitcoin

# Stop Oracle python server
#echo Oracle python server killing ...  
#fuser -k 8080/tcp

# Stop User Node
bitcoin-cli -datadir=./test/lsm/A/ stop
bitcoin-cli -datadir=./test/lsm/B/ stop
bitcoin-cli -datadir=./test/lsm/C/ stop
bitcoin-cli -datadir=./test/lsm/D/ stop
bitcoin-cli -datadir=./test/lsm/E/ stop

# Stop Oracle Node
bitcoin-cli -datadir=./test/lsm/O/ stop

# Clean data, remove generated blocks
echo Bitcoin regtest folders cleaning ... 
rm -rf ./test/lsm/*/regtest

echo STOP DONE