
#include <stdio.h>
#include <stdlib.h>  
#include <string.h>
#include <ourcontract.h>
#include <assert.h>




#define MAX_ACCOUNTS 100
#define MAX_ADDRESS_SIZE 256
#define MAX_QUEUE_CAPACITY 100

// Structures 


typedef struct Account {
    char address[MAX_ADDRESS_SIZE];
    int balance;
    int netBalance; // Net balance used during GridLock Resolution
} Account;

typedef struct OffsetTx {
    int id;
    char senderAddress[MAX_ADDRESS_SIZE];
    char receiverAddress[MAX_ADDRESS_SIZE];
    int amount;
} OffsetTx;

typedef struct Queue {
    int front, rear, size;
    unsigned capacity;
    OffsetTx transactions[MAX_QUEUE_CAPACITY];
} Queue;


typedef struct AccountQ{
    int front, rear, size;
    unsigned capacity;
    char addresses[MAX_ACCOUNTS][MAX_ADDRESS_SIZE]; 
} AccountQ;

// Contract state

typedef struct state {
    unsigned int size_contract; 
    unsigned int tempCounter ;
    unsigned int num_account;
    unsigned int num_active_queue;
    //unsgined int allocated_active_tx_queue_size;
    unsigned int num_inactive_queue;
    unsigned int num_account_queue;

} ContractState;


// Prototypes

    // Accounts prototypes
static void initAccounts();
static Account createAccount(char* address, int balance, int netBalance);
void printAccounts();
void printAccount(Account account);
static Account* findAccount(char *address);
int getNetBalance(char *address);
int setBalanceAndNetBalance(char *address, int amount);

    // OffsetTx prototypes
int createOffsetTx(char *senderAddress, char *receiverAddress, int amount);
void printOffsetTx(OffsetTx tx);
void printReturnOffsetTx(OffsetTx tx);
    // Queues prototypes
static void initQueue(unsigned capacity);
void resetQueue(Queue *queue,unsigned capacity);
void enqueue(Queue *queue, OffsetTx tx);
OffsetTx *dequeue(Queue *queue);
OffsetTx removeLatestTx(Queue * queue, char *address);
void toInactiveQueue(int index);
void toActiveQueue();
int isFull(Queue *queue);
int isEmpty(Queue *queue);
OffsetTx *getRear(Queue *queue);
OffsetTx *getFront(Queue *queue);
void printQueue(Queue *queue);
void printReturnQueue(Queue *queue);

    // Account Queue
static void initAccountQ(unsigned accountsCapacity);
void enqueueAccountQ(char  *address);
char *dequeueAccountQ();
int isFullAccountQ();
int isEmptyAccountQ();
int isInAccountQ(char *address);
void printAccountQ();

    // Gridlock 
void startGridLock();
void updateBalance();

// Global variables
Account *accounts;
int _account;
Queue *activeQueue;
Queue *inactiveQueue;
AccountQ *accountQueue;
ContractState theContractState;



// Contract Call functions 
int transfer(char* senderAddress, char* receiverAddress ,int amount);

// Contract State Read / Write
static unsigned int readState();
static unsigned int readContractState(unsigned char*, unsigned int);
static unsigned int readAccountArray(unsigned char*, unsigned int );
static unsigned int readActiveQueue(unsigned char*, unsigned int);
static unsigned int readInactiveQueue(unsigned char*, unsigned int);
static unsigned int readAccountsQueue(unsigned char*, unsigned int);

static unsigned int writeState();
static unsigned int writeContractStateToState(unsigned char*, unsigned int);
static unsigned int writeAccountArrayToState(unsigned char*, unsigned int);
static unsigned int writeActiveQueueToState(unsigned char*, unsigned int);
static unsigned int writeInactiveQueueToState(unsigned char*, unsigned int);
static unsigned int writeAccountQueueToState(unsigned char*, unsigned int);

static unsigned int compute_contract_size();

// Contract debug/utils prototypes
static int too_few_args()
{
    err_printf("[CONTRACT] too few args\n");
    return -1;
}


// Contract main function

int contract_main(int argc, char** argv)
{
    if (argc < 2 )
    {
        too_few_args();
        return -1;
    }

    if(!strcmp(argv[1], "init"))
    {
        // TODO : Save contract owner address (Oracle address) for future authorization

        err_printf("[CONTRACT] Init contract\n");
        initAccounts();
        initQueue(MAX_QUEUE_CAPACITY);    
        initAccountQ(MAX_ACCOUNTS);
        theContractState.size_contract = compute_contract_size();
        theContractState.tempCounter = 1;
        printAccounts();

        writeState();
    }
    else
    {
        readState();
        
        if(!strcmp(argv[1], "accounts")){
            printAccounts();
        }
        else if(!strcmp(argv[1], "activequeue")) {
            printQueue(activeQueue);
        }
        else if(!strcmp(argv[1], "inactivequeue")) {
            printQueue(inactiveQueue);
        }
        else if(!strcmp(argv[1], "accountqueue")){
            printAccountQ();
        }
        else if (!strcmp(argv[1], "setbalance")){
            if (argc < 4) {
                return too_few_args();
            }
            err_printf("[CONTRACT] set balance : %d\n", setBalanceAndNetBalance(argv[2], atoi(argv[3])));
        }
        else if(!strcmp(argv[1], "transfer"))
        {
            if (argc < 5){
               return too_few_args();
            }
            err_printf("[CONTRACT] transfer : %d\n", transfer(argv[2], argv[3], atoi(argv[4])));
        }
        else if (!strcmp(argv[1], "gridlock")){
            startGridLock();    
        }
        else {
            err_printf("[CONTRACT] error : command not found : %s\n", argv[1]);
            return 0;
        }
        // if case 2 (remove TX )
        // if case 3 (reorder TX )




        theContractState.size_contract = compute_contract_size();
        writeState();
    }
    return 0;
}



static void initAccounts(){
    accounts = malloc(sizeof(Account) * MAX_ACCOUNTS);
    theContractState.num_account = 0;
    // Quorum Ubin Test case
    /*
    accounts[0] = createAccount("A", 3000, 3000);
    accounts[1] = createAccount("B", 4000, 4000);
    accounts[2] = createAccount("C", 5000, 5000);
    accounts[3] = createAccount("D", 4000, 4000);
    accounts[4] = createAccount("E", 3000, 3000);
    */    

   // FISC Test case
   /*
    accounts[0] = createAccount("A", 0, 0);
    accounts[1] = createAccount("B", 0, 0);
    accounts[2] = createAccount("C", 3000, 3000);
    accounts[3] = createAccount("D", 0, 0);
    accounts[4] = createAccount("E", 0, 0);
    accounts[5] = createAccount("F", 0, 0);
    accounts[6] = createAccount("G", 0, 0);
    accounts[7] = createAccount("H", 0, 0);
    */


   // Test case with python tool. Initialize balance and net balance to 0. Whenever users send their inputs (in real tx) to Oracle, Oracle will call the smart contract to update their balance.
    accounts[0] = createAccount("A", 0, 0);
    accounts[1] = createAccount("B", 0, 0); 
    accounts[2] = createAccount("C", 0, 0);
    accounts[3] = createAccount("D", 0, 0);
    accounts[4] = createAccount("E", 0, 0);
}



static Account createAccount(char* address, int balance, int netBalance)
{
    Account account;
    strcpy(account.address, address);
    account.balance = balance;
    account.netBalance = netBalance;

    theContractState.num_account ++;

    return account;
}

void printAccounts()
{
    err_printf("[CONTRACT] ACCOUNTS BALANCE STATES : \n");
    for(int i = 0 ; i < theContractState.num_account ; i++)
    {
        
        err_printf("address : %s, balance : %d, netBalance  : %d \n", accounts[i].address, accounts[i].balance, accounts[i].netBalance);
        out_printf("address : %s, balance : %d, netBalance  : %d \n", accounts[i].address, accounts[i].balance, accounts[i].netBalance);
    }
}

void printAccount(Account account){
    
    err_printf("[CONTRACT] Address : %s, balance : %d, netBalance : %d \n", account.address, account.balance, account.netBalance);
}

static Account* findAccount(char *address)
{
    for(int i = 0; i < theContractState.num_account ; i ++) {
        if(!strcmp(accounts[i].address , address))
        {
            return &accounts[i];
        }
    }
    return NULL;
}

int getNetBalance(char *address)
{
    for(int i  = 0 ; i < theContractState.num_account ; i++)
    {
        if (!strcmp(accounts[i].address,address))
        {
            err_printf("[CONTRACT] Get net balance call : \n");
            printAccount(accounts[i]);
            
            return accounts[i].netBalance;
        }
    }
    err_printf("[CONTRACT] Address does not exist\n");
    return -1;
}



int setBalanceAndNetBalance(char *address, int amount)
{
    
    Account *account = findAccount(address);
    if(account == NULL){
        err_printf("[CONTRACT] Sender Account not found : %s\n", address);
        return -1;
    }
    account->balance += amount;
    account->netBalance += amount;
    err_printf("[CONTRACT] %s balance and net balance set to %d\n", address, amount);
    return 0;
}



int createOffsetTx(char *senderAddress, char *receiverAddress, int amount)
{
    
    if (amount <= 0 ) {
        err_printf("[CONTRACT] Amount must be strictly positive \n");
        return -1;
    };

    Account *sender = findAccount(senderAddress);
    if(sender == NULL){
        err_printf("[CONTRACT] Sender Account not found : %s\n", senderAddress);
        return -1;
    }

    Account *receiver = findAccount(receiverAddress);
    if(receiver == NULL){
        err_printf("[CONTRACT] Receiver Account not found : %s\n", senderAddress);
        return -1;
    }

    
    OffsetTx tx;
    
    // TODO Generate TXID
    tx.id = theContractState.tempCounter ;
    theContractState.tempCounter++;
    strcpy(tx.receiverAddress, receiverAddress);
    strcpy(tx.senderAddress, senderAddress);
    tx.amount  = amount;


    sender->netBalance -= amount;
    receiver->netBalance += amount;
    
    enqueue(activeQueue, tx);

    if( !isInAccountQ(sender->address)){
        enqueueAccountQ(sender->address);
    }
    
    return 0;
}


// Display a transaction information : id, senderAddress, receiverAddress, amount
void printOffsetTx(OffsetTx tx)
{
    err_printf("[CONTRACT] tx  : %d, sender : %s, receiver :  %s, amount %d \n", tx.id, tx.senderAddress, tx.receiverAddress, tx.amount);
    
}

// Display a transaction information : id, senderAddress, receiverAddress, amount
// And use STDOUT to retrieve by calling the contract in another process (oracleContract.py)
void printReturnOffsetTx(OffsetTx tx)
{
    err_printf("[CONTRACT] tx  : %d, sender : %s, receiver :  %s, amount %d \n", tx.id, tx.senderAddress, tx.receiverAddress, tx.amount);
    
    // output the solution in stdout (will be captured by main python script oracleContract.py)
    // NB : err_printf seems to flush STDOUT right away 
    printf("%d,%s,%s,%d \n", tx.id, tx.senderAddress, tx.receiverAddress, tx.amount);
}

static void initQueue(unsigned capacity){
    activeQueue = (Queue*) malloc(sizeof(Queue));
    activeQueue->capacity = capacity;
    activeQueue->size = 0;
    activeQueue->rear = capacity - 1;
    activeQueue->front = 0;

    inactiveQueue = (Queue*) malloc(sizeof(Queue));
    inactiveQueue->capacity = capacity;
    inactiveQueue->size = 0;
    inactiveQueue->rear = capacity - 1;
    inactiveQueue->front = 0;
    //queue->transactions = (OffsetTx*) malloc(sizeof(capacity * sizeof(OffsetTx)));
}

void resetQueue(Queue *queue, unsigned  capacity)
{
    err_printf("[CONTRACT] QUEUE RESET \n");
    queue->size = 0;
    queue->front = 0;
    queue->rear = capacity - 1;

}

void enqueue(Queue *queue,OffsetTx tx){
    if(isFull(queue)) return;
    
    queue->rear = (queue->rear + 1 ) % queue->capacity;
    queue->transactions[queue->rear] = tx;
    queue->size++;
    err_printf("[CONTRACT] Enqueued TX  : ");
    printOffsetTx(tx);
}

OffsetTx *dequeue(Queue *queue ){
    
    if(isEmpty(queue)) return NULL;
    OffsetTx *tx = & (queue->transactions[queue->front]);
    queue->front = (queue->front + 1 ) % queue->capacity;
    queue->size--;
    err_printf("[CONTRACT] Dequeued TX  : ");
    printOffsetTx(*tx);
    return tx;
   

}

OffsetTx removeLatestTx(Queue *queue, char *address)
{
    //if(isEmpty(queue)) return ;
    Account *senderAccount;
    Account *receiverAccount;
    OffsetTx tx ;
    int txIndex;

    // From rear to front queue (latest to oldest)
    //err_printf("[CONTRACT] ACTIVE QUEUE STATE :\n");
    //printQueue(queue);

    for(int i = queue->rear ; i > queue->front - 1 ; i-- )
    {   
        /*
        printf("Queue index : %d\n",i);
        printOffsetTx(queue->transactions[i]);
        printf("address : %s\n", address);*/

        if( !strcmp(queue->transactions[i].senderAddress, address ))
        {
       
            tx  =  (queue->transactions[i]);
            txIndex = i;
            break;
        }

    }
    err_printf("[CONTRACT] REMOVED TX : \n");
    printOffsetTx(tx);
    toInactiveQueue(txIndex);

    // Update the sender/receiver balance with the removed tx
    senderAccount = findAccount(tx.senderAddress);
    senderAccount->netBalance += tx.amount;
    receiverAccount = findAccount(tx.receiverAddress);
    receiverAccount->netBalance -= tx.amount;
    // Enqueue the receiver in the account queue as its balance decreased
    enqueueAccountQ(receiverAccount->address);

    
    return tx;
}

// Insert in inactive queue a transaction by its index
void toInactiveQueue(int index){

    enqueue(inactiveQueue, activeQueue->transactions[index]);

    // Remove the transaction from active queue by index
    for(int i = index ; i < activeQueue->rear   ; i++ )
    {
        activeQueue->transactions[i] = activeQueue->transactions[i+1];
    } 
    activeQueue->rear = activeQueue->rear - 1;
    activeQueue->size--;
}

// Insert ALL transactions from the inactive queue to the active queue (called after right after gridlock)
// Update the net balance form the pushed transactions
// Reset inactive queue
void toActiveQueue()
{
    err_printf("[CONTRACT] PUSH BACK TX inactiveQueue to activeQueue\n");
    //memcpy(inactiveQueue, activeQueue, sizeof(Queue));
    
    activeQueue->rear = inactiveQueue->rear;
    activeQueue-> front = inactiveQueue->front;
    activeQueue->size = inactiveQueue->size;

    
    // Reorder 
    // Get minimum index (Queue structure is a circular queue. front and rear attributes can be both min or max index)
    int minIndex, maxIndex;
    if (inactiveQueue->front > inactiveQueue->rear)
    {
        minIndex = inactiveQueue->rear;
        maxIndex = inactiveQueue->front;
    }
    else{
        minIndex = inactiveQueue->front;
        maxIndex = inactiveQueue->rear;
    }
    
    OffsetTx tx;
    Account* senderAccount;
    Account* receiverAccount;
    for(int i = minIndex ; i < maxIndex + 1 ; i++){
        // Insert inactive queue tx back in active queue
        tx = inactiveQueue->transactions[maxIndex + minIndex - i];
        activeQueue->transactions[i] = tx;
        // Update balance back (NB : transactions already in the queue therefore no need to enqueue it)
        senderAccount = findAccount(tx.senderAddress);
        if (senderAccount == NULL) {
            err_printf("[CONTRACT] %s account not found\n", tx.senderAddress);
        }

        receiverAccount = findAccount(tx.receiverAddress);
        if (receiverAccount == NULL) {
            err_printf("[CONTRACT] %s account not found\n", tx.receiverAddress);
        }

        senderAccount->netBalance -= tx.amount;
        receiverAccount->netBalance += tx.amount;

        if( !isInAccountQ(senderAccount->address)){
            enqueueAccountQ(senderAccount->address);
        }
    }
    
    // Reset inactive queue
    err_printf("[CONTRACT] INACTIVE RESET QUEUE\n", tx.receiverAddress);
    resetQueue(inactiveQueue, MAX_QUEUE_CAPACITY);
    

}

int isFull(Queue *queue){
    return (queue->size == queue->capacity);
}

int isEmpty(Queue *queue){
    return (queue->size == 0);
}

OffsetTx *getRear(Queue *queue){
    if(isEmpty(queue)) return NULL;
    OffsetTx *tx =  & (queue->transactions[queue->rear]);
    printf("Rear element : %d, %s, %s, %d \n", tx->id, tx->senderAddress, tx->receiverAddress, tx->amount);
    return tx;
   
}
OffsetTx *getFront(Queue *queue){
    if(isEmpty(queue)) return NULL;
    OffsetTx *tx =  &(queue->transactions[queue->front]);
    printf("Front element : %d, %s, %s, %d \n", tx->id, tx->senderAddress, tx->receiverAddress, tx->amount);
    return tx;
}


void printQueue(Queue *queue){
    if (isEmpty(queue)) {err_printf("[CONTRACT] The queue is empty.\n");return;}
    err_printf("[CONTRACT] QUEUE STATE : \n");
    for (int i = queue->front ; i < queue->rear + 1 ; i++)
    {
        printOffsetTx( (queue->transactions)[i]);
    }
}

void printReturnQueue(Queue *queue){
    if (isEmpty(queue)) {err_printf("[CONTRACT] The queue is empty.\n");return;}
    err_printf("[CONTRACT] QUEUE STATE : \n");
    for (int i = queue->front ; i < queue->rear + 1 ; i++)
    {
        printReturnOffsetTx( (queue->transactions)[i]);
    }
}



static void initAccountQ(unsigned accountsCapacity){
    accountQueue =  (AccountQ*) malloc(sizeof(AccountQ));
    accountQueue->capacity = accountsCapacity;
    accountQueue->size = 0;
    accountQueue->rear = accountsCapacity - 1;
    accountQueue->front = 0;
   // accountQueue->accounts = (Account*) malloc(sizeof(accountsCapacity * sizeof(Account)));

}

void enqueueAccountQ(char *address)
{
    if(isFullAccountQ()) return;

    accountQueue->rear = (accountQueue->rear + 1 ) % accountQueue->capacity;

    strcpy(accountQueue->addresses[accountQueue->rear], address) ;
    accountQueue->size++;
    err_printf("[CONTRACT] Enqueued account : ");
    err_printf("%s\n", accountQueue->addresses[accountQueue->rear]);
}
char *dequeueAccountQ()
{
    if(isEmptyAccountQ()) return NULL;
    char *address = accountQueue->addresses[accountQueue->front];
    accountQueue->front = (accountQueue->front + 1 ) % accountQueue->capacity;
    accountQueue->size--;
    err_printf("[CONTRACT] Dequeued account : ");
    err_printf("%s\n", address );
    return address;
}

int isFullAccountQ(){
    return (accountQueue->size == accountQueue->capacity);
}

int isEmptyAccountQ(){
    return (accountQueue->size == 0);
}

int isInAccountQ(char *address){
    for(int i = accountQueue->front ; i < accountQueue->rear + 1 ; i++)
    {
        if( !strcmp(accountQueue->addresses[i],address) )
        {
            return 1;
        }
    }
    return 0;
}


void printAccountQ(){
    if (isEmptyAccountQ()) {err_printf("[CONTRACT] The account queue is empty.\n");return;}
    err_printf("[CONTRACT] ACCOUNT QUEUE STATE : \n");
    for (int i = accountQueue->front ; i < accountQueue->rear + 1 ; i++)
    {
        err_printf("%s\n", accountQueue->addresses[i]);
    }
}



void startGridLock()
{   
    char *currentAddress;
    err_printf("[CONTRACT] Gridlock starting ... -------------------------------------- \n");
    while( accountQueue->size > 0)
    {
        currentAddress = dequeueAccountQ();

        
        if (getNetBalance(currentAddress) >= 0) 
            continue;

        while (getNetBalance(currentAddress) < 0) 
            removeLatestTx(activeQueue, currentAddress);

    }

    // Update balance
    if (!isEmpty(activeQueue))
    {
        err_printf("\n[CONTRACT] SOLUTION FOUND\n");
        err_printf("[CONTRACT] ACTIVE QUEUE\n");
        printReturnQueue(activeQueue);
        err_printf("[CONTRACT] INACTIVE QUEUE\n"); 
        printQueue(inactiveQueue);

        updateBalance();
                
    }
    else
        err_printf("\n[CONTRACT] NO SOLUTION FOUND\n");
    
    
    err_printf("[CONTRACT] GRIDLOCK HAS ENDED --------------------------------------\n");
    if (inactiveQueue->size > 0)
    {
        toActiveQueue();
        printAccounts();
    }
}


// Reset balance and net balance from remaining accounts in the solution
void updateBalance()
{
    printAccounts();
    err_printf("[CONTRACT] UPDATING THE BALANCE (reset active queue and send the final tx) ...\n");

   Account *activeAccount;
   for (int i = activeQueue->front ; i < activeQueue->rear + 1 ; i++)
   {
       activeAccount = findAccount( (activeQueue->transactions[i]).senderAddress );
       activeAccount->balance = 0;
       activeAccount->netBalance = 0;
   }

    resetQueue(activeQueue, MAX_QUEUE_CAPACITY);
}

// Contract call functions

int transfer(char* senderAddress, char* receiverAddress ,int amount)
{
    Account* senderAccount = findAccount(senderAddress);
    if (senderAccount == NULL) {
        err_printf("%s account not found\n", senderAddress);
        return -1;
    }

    Account* receiverAccount = findAccount(receiverAddress);
    if (receiverAccount == NULL) {
        err_printf("%s account not found\n", receiverAddress);
        return -1;
        //appendToAccountArray(createAccount(receiverAddress));
        //receiverAccount = findAccount(receiverAddress);

    }

    if (senderAccount->balance >= amount && amount > 0) {
        receiverAccount->balance += amount;
        receiverAccount->netBalance += amount;
        senderAccount->balance -= amount;
        senderAccount->netBalance -= amount;
        return 0;
    }

    err_printf("[CONTRACT] insufficient funds\n");
    int res = createOffsetTx(senderAddress,receiverAddress,amount);
    return res;
}

// ------------------Contract State Read / Write

static unsigned int readState(){
    /*
        Use state_read() to read your program data
        The data are stored in memory, tight together with UTXO so it will revert automatically

        state_read(buff, size) is straightforward: read `size` bytes to `buff`
        The point is how you define your structure and serialize it

        The following code is just one of the way to read state
            * In write stage: 
            * you first write how many byte you stored
            * then write all your data
            * In read stage:
            * first get the size of data
            * then get all the data
            * unserialize the data    
    */

    unsigned int count;
    state_read(&count, sizeof(int));

    unsigned char* buff = malloc(sizeof(char) * count);
    unsigned int offset = 0;
    state_read(buff, count);
    
    offset += readContractState(buff, offset);
    offset += readAccountArray(buff, offset);
    offset += readActiveQueue(buff, offset);
    offset += readInactiveQueue(buff, offset);
    offset += readAccountsQueue(buff, offset);

    assert(offset == count);
    return offset;
}

static unsigned int readContractState(unsigned char* buffer, unsigned int offset)
{
    memcpy(&theContractState, buffer+offset, sizeof(ContractState));
    return sizeof(ContractState);
}

static unsigned int readAccountArray(unsigned char* buffer, unsigned int offset)
{
    accounts = malloc(sizeof(Account) * MAX_ACCOUNTS);
    memcpy(accounts, buffer+offset, sizeof(Account) * MAX_ACCOUNTS);
    return sizeof(Account) * MAX_ACCOUNTS;
}

static unsigned int readActiveQueue(unsigned char* buffer, unsigned int offset)
{
    //globalAllowanceArray = malloc(sizeof(Allowance) * theContractState.allocated_allowance_array_size);
    activeQueue = (Queue*) malloc(sizeof(Queue));
    memcpy(activeQueue, buffer+offset, sizeof(Queue));
    return sizeof(Queue);
}
static unsigned int readInactiveQueue(unsigned char* buffer, unsigned int offset)
{
    inactiveQueue = (Queue*) malloc(sizeof(Queue));
    memcpy(inactiveQueue, buffer+offset, sizeof(Queue));
    return sizeof(Queue);
}
static unsigned int readAccountsQueue(unsigned char* buffer, unsigned int offset)
{
    accountQueue = (AccountQ*) malloc(sizeof(AccountQ));
    memcpy(accountQueue, buffer+offset, sizeof(AccountQ));
    return sizeof(AccountQ);
}


static unsigned int writeState()
{
    /*
        Use state_write() to write your program data
        The data are stored in memory, tight together with UTXO so it will revert automatically

        state_read(buff, size) is straightforward: write `size` bytes from `buff`
        
        Warning: You need to write all your data at once. 
        The state is implement as a vector, and will resize every time you use state_write
        So if you write multiple times, it will be the size of last write

        One way to solve this is you memcpy() all your serialized data to a big array
        and then call only one time state_write()
    */

    unsigned char *buff = malloc(sizeof(int) + sizeof(char) * theContractState.size_contract);
    unsigned int offset = 0;

    memcpy(buff, &theContractState.size_contract, sizeof(int));
    offset += sizeof(int);

    offset += writeContractStateToState(buff, offset);
    offset += writeAccountArrayToState(buff, offset);
    offset += writeActiveQueueToState(buff, offset);
    offset += writeInactiveQueueToState(buff, offset);
    offset += writeAccountQueueToState(buff, offset);
    
    assert(offset == sizeof(int) + sizeof(char)* theContractState.size_contract);
    state_write(buff, offset);
    return offset;
}

static unsigned int writeContractStateToState(unsigned char* buffer, unsigned int offset)
{
    memcpy(buffer+offset, &theContractState, sizeof(ContractState));
    return sizeof(ContractState);
}

static unsigned int writeAccountArrayToState(unsigned char* buffer, unsigned int offset)
{    
    memcpy(buffer+offset, accounts, sizeof(Account) * MAX_ACCOUNTS);
    return sizeof(Account) * MAX_ACCOUNTS;
}

static unsigned int writeActiveQueueToState(unsigned char* buffer, unsigned int offset)
{    
    memcpy(buffer+offset, activeQueue, sizeof(Queue) );
    return sizeof(Queue);
}

static unsigned int writeInactiveQueueToState(unsigned char* buffer, unsigned int offset)
{    
    memcpy(buffer+offset, inactiveQueue, sizeof(Queue) );
    return sizeof(Queue);
}

static unsigned int writeAccountQueueToState(unsigned char* buffer, unsigned int offset)
{    
    memcpy(buffer+offset, accountQueue, sizeof(AccountQ) );
    return sizeof(AccountQ);
}


static unsigned int compute_contract_size()
{
    unsigned int size_sum = 0;

    
    unsigned int sz_contract_state = sizeof(ContractState);
    unsigned int sz_account_array = sizeof(Account) * MAX_ACCOUNTS;
    unsigned int sz_active_queue = sizeof(Queue);
    unsigned int sz_inactive_queue = sizeof(Queue);
    unsigned int sz_account_queue = sizeof(AccountQ);

    size_sum =  sz_contract_state + sz_account_array + sz_active_queue + sz_inactive_queue + sz_account_queue;
    return size_sum;
}