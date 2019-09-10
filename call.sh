caller_path=./example/caller.c
callee_path=./example/callee.c

# 兩次比較保險
sudo kill -9 $(ps aux | grep bitcoind | sed -n '1p' | awk '{print $2;}') 2>/dev/null
sudo kill -9 $(ps aux | grep bitcoind | sed -n '2p' | awk '{print $2;}') 2>/dev/null
rm ~/.bitcoin/regtest -rf
rm ~/.bitcoin/blocks -rf
killall ourcontract-rt
killall ourcontract-rt
bitcoind -regtest -txindex -reindex -daemon

sleep 3
bitcoin-cli generate 101 > /dev/null

bitcoin-cli  -regtest deploycontract ${caller_path} 0
bitcoin-cli  -regtest deploycontract ${callee_path} 0
rm ~/.bitcoin/regtest/contracts/err
bitcoin-cli generate 1 > /dev/null

echo -e "\n---------------------- err ----------------------------\n"
cat ~/.bitcoin/regtest/contracts/err
echo -e "-------------------------------------------------------\n\n"

read -p "caller: " caller
read -p "callee: " callee

export caller=$caller
export callee=$callee

echo -e "\n"
bitcoin-cli -regtest callcontract $caller 3 $caller $callee
bitcoin-cli generate 10 > /dev/null

echo -e "\n---------------------- err ----------------------------\n"
cat ~/.bitcoin/regtest/contracts/err
echo -e "-------------------------------------------------------\n\n"
