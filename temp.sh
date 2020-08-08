
'
ourcontract-mkdll contracts lsm
ourcontract-rt contracts lsm init
ourcontract-rt contracts lsm setbalance A 50
ourcontract-rt contracts lsm transfer B A 50
ourcontract-rt contracts lsm transfer C A 50
ourcontract-rt contracts lsm transfer D A 50
ourcontract-rt contracts lsm gridlock
echo "[BASH] active Queue"
ourcontract-rt contracts lsm activequeue
echo "[BASH] inactive Queue"
ourcontract-rt contracts lsm inactivequeue
'


ourcontract-mkdll contracts lsm
ourcontract-rt contracts lsm init
ourcontract-rt contracts lsm setbalance A 50
ourcontract-rt contracts lsm setbalance B 100

ourcontract-rt contracts lsm transfer A B 100
ourcontract-rt contracts lsm transfer B A 150
ourcontract-rt contracts lsm gridlock
echo "[BASH] active Queue"
ourcontract-rt contracts lsm activequeue
echo "[BASH] inactive Queue"
ourcontract-rt contracts lsm inactivequeue
