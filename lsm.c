
#include <stdio.h>
#include <stdlib.h>  
#include <string.h>
#include <inttypes.h>



#define MAX_ACCOUNTS 100
#define MAX_ADDRESS_SIZE 256
#define MAX_QUEUE_CAPACITY 100

// Structures 


typedef struct Account {
    char address[MAX_ADDRESS_SIZE];
    int balance;
    int netBalance; // Net balance used during GridLock Resolution
    // todo add list of pending tx ?
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

// Prototypes

    // Accounts prototypes
static void initAccounts();
static Account createAccount(char* address, int balance, int netBalance);
void printAccounts();
void printAccount(Account account);
static Account* findAccount(char *address);
int getNetBalance(char *address);

    // OffsetTx prototypes
int createOffsetTx(char *senderAddress, char *receiverAddress, int amount);
void printOffsetTx(OffsetTx tx);

    // Queues prototypes
static void initQueue(unsigned capacity);
void enqueue(Queue *queue, OffsetTx tx);
OffsetTx *dequeue(Queue *queue);
OffsetTx removeLatestTx(Queue * queue, char *address);
void toInactiveQueue(int index);
int isFull(Queue *queue);
int isEmpty(Queue *queue);
OffsetTx *getRear(Queue *queue);
OffsetTx *getFront(Queue *queue);
void printQueue(Queue *queue);

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

// Global variables
Account *accounts;
int accountsLength;
Queue *activeQueue;
AccountQ *accountQueue;
Queue *inactiveQueue;

int tempCounter = 0;

int main()
{
    initAccounts();
    printAccounts();

    initQueue(MAX_QUEUE_CAPACITY);    
    initAccountQ(MAX_ACCOUNTS);

    printQueue(activeQueue);
    printAccountQ();

       
    
    createOffsetTx("0xA", "0xB", 5000);
    createOffsetTx("0xB", "0xC", 6000);
    createOffsetTx("0xB", "0xC", 30000);
    createOffsetTx("0xC", "0xD", 8000);
    createOffsetTx("0xC", "0xE", 80000);
    createOffsetTx("0xD", "0xE", 7000);
    createOffsetTx("0xA", "0xC", 6000);
    createOffsetTx("0xE", "0xA", 8000);
    createOffsetTx("0xE", "0xB", 100000);
    createOffsetTx("0xD", "0xA", 5000);


    printQueue(activeQueue);
    printAccounts();
    printAccountQ();

    startGridLock();
    
    return 0;
};

static void initAccounts(){
    accounts = malloc(sizeof(Account) * MAX_ACCOUNTS);
    accountsLength = 0;

    accounts[0] = createAccount("0xA", 3000, 3000);
    accounts[1] = createAccount("0xB", 4000, 4000);
    accounts[2] = createAccount("0xC", 5000, 5000);
    accounts[3] = createAccount("0xD", 4000, 4000);
    accounts[4] = createAccount("0xE", 3000, 3000);



}



static Account createAccount(char* address, int balance, int netBalance)
{
    Account account;
    strcpy(account.address, address);
    account.balance = balance;
    account.netBalance = netBalance;

    accountsLength++;

    return account;
}

void printAccounts()
{
    printf("ACCOUNTS BALANCE STATES : \n");
    for(int i = 0 ; i < accountsLength ; i++)
    {
        
        printf("address : %s, balance : %d, netBalance  : %d \n", accounts[i].address, accounts[i].balance, accounts[i].netBalance);
    }
}

void printAccount(Account account){
    
    printf("%s, %d, %d \n", account.address, account.balance, account.netBalance);
}

static Account* findAccount(char *address)
{
    for(int i = 0; i < accountsLength ; i ++) {
        if(!strcmp(accounts[i].address , address))
        {
            return &accounts[i];
        }
    }
    return NULL;
}

int getNetBalance(char *address)
{
    for(int i  = 0 ; i < accountsLength ; i++)
    {
        if (!strcmp(accounts[i].address,address))
        {
            printf("Get net balance call : \n");
            printAccount(accounts[i]);
            
            return accounts[i].netBalance;
        }
    }
    printf("Address does not exist\n");
    return -1;
}



int createOffsetTx(char *senderAddress, char *receiverAddress, int amount)
{
    
    if (amount <= 0 ) {
        printf("Amount must be strictly positive \n");
        return -1;
    };

    Account *sender = findAccount(senderAddress);
    if(sender == NULL){
        printf("Sender Account not found : %s\n", senderAddress);
        return -1;
    }

    Account *receiver = findAccount(receiverAddress);
    if(receiver == NULL){
        printf("Receiver Account not found : %s\n", senderAddress);
        return -1;
    }

    
    OffsetTx tx;
    
    // TODO Generate TXID
    tx.id = tempCounter;
    tempCounter++;
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

void printOffsetTx(OffsetTx tx)
{
    printf("%d, %s, %s, %d \n", tx.id, tx.senderAddress, tx.receiverAddress, tx.amount);
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


void enqueue(Queue *queue,OffsetTx tx){
    if(isFull(queue)) return;
    
    queue->rear = (queue->rear + 1 ) % queue->capacity;
    queue->transactions[queue->rear] = tx;
    queue->size++;
    printf("Enqueued TX  : ");
    printOffsetTx(tx);
}

OffsetTx *dequeue(Queue *queue ){
    
    if(isEmpty(queue)) return NULL;
    OffsetTx *tx = & (queue->transactions[queue->front]);
    queue->front = (queue->front + 1 ) % queue->capacity;
    queue->size--;
    printf("Dequeued TX  : ");
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
    printf("ACTIVE QUEUE STATE :\n");
    printQueue(queue);

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
    printf("REMOVED TX : \n");
    printOffsetTx(tx);

    toInactiveQueue(txIndex);

    senderAccount = findAccount(tx.senderAddress);
    senderAccount->netBalance += tx.amount;
    receiverAccount = findAccount(tx.receiverAddress);
    receiverAccount->netBalance -= tx.amount;
    enqueueAccountQ(receiverAccount->address);

    
    return tx;
}

void toInactiveQueue(int index){

    enqueue(inactiveQueue, activeQueue->transactions[index]);
    for(int i = index ; i < activeQueue->rear   ; i++ )
    {
        activeQueue->transactions[i] = activeQueue->transactions[i+1];
    } 
    activeQueue->rear = activeQueue->rear - 1;
    activeQueue->size--;
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
    if (isEmpty(queue)) {printf("The queue is empty.\n");return;}
    printf("QUEUE STATE : \n");
    for (int i = queue->front ; i < queue->rear + 1 ; i++)
    {
        printOffsetTx( (queue->transactions)[i] );
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
    printf("Enqueued account : ");
    printf("%s\n", accountQueue->addresses[accountQueue->rear]);
}
char *dequeueAccountQ()
{
    if(isEmptyAccountQ()) return NULL;
    char *address = accountQueue->addresses[accountQueue->front];
    accountQueue->front = (accountQueue->front + 1 ) % accountQueue->capacity;
    accountQueue->size--;
    printf("Dequeued account : ");
    printf("%s\n", address );
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
    if (isEmptyAccountQ()) {printf("The account queue is empty.\n");return;}
    printf("ACCOUNT QUEUE STATE : \n");
    for (int i = accountQueue->front ; i < accountQueue->rear + 1 ; i++)
    {
        printf("%s\n", accountQueue->addresses[i]);
    }
}



void startGridLock()
{   
    char *currentAddress;
    OffsetTx removedTx;
    printf("Gridlock starting ... ------------------------------- \n");
    while( accountQueue->size > 0)
    {
        currentAddress = dequeueAccountQ();

        
        if (getNetBalance(currentAddress) >= 0) continue;

        while (getNetBalance(currentAddress) < 0) 
        {
            removedTx = removeLatestTx(activeQueue, currentAddress);
            
        }
        //if( !strcmp(currentAddress,"0xC")) break;
        
    }

    printf("Gridlock has ended ... -------------------------------\n");
    printf("ACTIVE QUEUE\n");
    printQueue(activeQueue);
    printf("INACTIVE QUEUE\n"); // TODO : inactive queue state should be ordered.
    printQueue(inactiveQueue);
    printAccounts();
    // Settle remaining TX in the active queue
}