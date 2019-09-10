file=vote.c

sudo kill -9 $(ps aux | grep bitcoind | sed -n '1p' | awk '{print $2;}') 2>/dev/null
sudo kill -9 $(ps aux | grep bitcoind | sed -n '2p' | awk '{print $2;}') 2>/dev/null
rm ~/.bitcoin/regtest -rf
rm ~/.bitcoin/blocks -rf
killall ourcontract-rt
killall ourcontract-rt
bitcoind -regtest -txindex -reindex -daemon

sleep 3
bitcoin-cli generate 101
sleep 5
bitcoin-cli deploycontract ${file} | tee tmp
bitcoin-cli generate 1
bitcoin-cli callcontract "$(ls ~/.bitcoin/regtest/contracts | sed -n '1p')" "sign_up" "myname1" "mykey1" 
bitcoin-cli generate 1
bitcoin-cli callcontract "$(ls ~/.bitcoin/regtest/contracts | sed -n '1p')" "sign_up" "myname2" "mykey2" 
bitcoin-cli generate 1
bitcoin-cli callcontract "$(ls ~/.bitcoin/regtest/contracts | sed -n '1p')" "sign_up" "myname3" "mykey3"
bitcoin-cli generate 1
bitcoin-cli callcontract "$(ls ~/.bitcoin/regtest/contracts | sed -n '1p')" "freeze"  "myname1" "mykey1"  
bitcoin-cli generate 1
bitcoin-cli dumpcontractmessage $(cat tmp | sed -n '3p' | awk '{print $3}' | cut -d '"' -f 2)
