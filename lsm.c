
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

    // OffsetTx prototypes
int createOffsetTx(char *senderAddress, char *receiverAddress, int amount);
void printOffsetTx(OffsetTx tx);

    // Queues prototypes
static void initQueue(unsigned capacity);
void enqueue(OffsetTx tx);
OffsetTx *dequeue();
int isFull();
int isEmpty();
OffsetTx *getRear();
OffsetTx *getFront();
void printQueue();

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
Queue *queue;
AccountQ *accountQueue;
Queue *inactiveQueue;

int main()
{
    initAccounts();
    printAccounts();

    initQueue(MAX_QUEUE_CAPACITY);
    initAccountQ(MAX_ACCOUNTS);

    // Queue test
    printQueue();
    printAccountQ();

       
    
    createOffsetTx("0x1234", "0x5678", 2000);

    createOffsetTx("0x5678", "0x1234", 2500);
    createOffsetTx("0x8888", "0x5678", 4000);
    createOffsetTx("0x9999", "0x5678", 4500);
    createOffsetTx("0x5678", "0x9999", 2500);
    getRear();
    getFront();
    dequeue();
    dequeue();
    printQueue();
    printAccounts();
    printAccountQ();


    return 0;
};

static void initAccounts(){
    accounts = malloc(sizeof(Account) * MAX_ACCOUNTS);
    accountsLength = 0;

    accounts[0] = createAccount("0x1234", 1000, 1000);
    accounts[1] = createAccount("0x5678", 2000, 2000);
    accounts[2] = createAccount("0x8888", 3000, 3000);
    accounts[3] = createAccount("0x9999", 4000, 4000);



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
    tx.id = 0;
    strcpy(tx.receiverAddress, receiverAddress);
    strcpy(tx.senderAddress, senderAddress);
    tx.amount  = amount;


    sender->netBalance -= amount;
    receiver->netBalance += amount;
    
    enqueue(tx);

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
    queue = (Queue*) malloc(sizeof(Queue));
    queue->capacity = capacity;
    queue->size = 0;
    queue->rear = capacity - 1;
    queue->front = 0;
    //queue->transactions = (OffsetTx*) malloc(sizeof(capacity * sizeof(OffsetTx)));
}


void enqueue(OffsetTx tx){
    if(isFull()) return;
    
    queue->rear = (queue->rear + 1 ) % queue->capacity;
    queue->transactions[queue->rear] = tx;
    queue->size++;
    printf("Enqueued element : ");
    printOffsetTx(tx);
}

OffsetTx *dequeue(){
    if(isEmpty()) return NULL;
    OffsetTx *tx = & (queue->transactions[queue->front]);
    queue->front = (queue->front + 1 ) % queue->capacity;
    queue->size--;
    printf("Dequeued element : ");
    printOffsetTx(*tx);
    return tx;
   

}

int isFull(){
    return (queue->size == queue->capacity);
}

int isEmpty(){
    printf("Queue size : %d\n", queue->size);
    return (queue->size == 0);
}

OffsetTx *getRear(){
    if(isEmpty()) return NULL;
    OffsetTx *tx =  & (queue->transactions[queue->rear]);
    printf("Rear element : %d, %s, %s, %d \n", tx->id, tx->senderAddress, tx->receiverAddress, tx->amount);
    return tx;
   
}
OffsetTx *getFront(){
    if(isEmpty()) return NULL;
    OffsetTx *tx =  &(queue->transactions[queue->front]);
    printf("Front element : %d, %s, %s, %d \n", tx->id, tx->senderAddress, tx->receiverAddress, tx->amount);
    return tx;
}

void printQueue(){
    if (isEmpty()) {printf("The queue is empty.\n");return;}
    printf("Queue size %d\n", queue->size);
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
    printf("Account Enqueued element : ");
    printf("%s\n", accountQueue->addresses[accountQueue->rear]);
}
char *dequeueAccountQ()
{
    if(isEmptyAccountQ()) return NULL;
    char *address = accountQueue->addresses[accountQueue->front];
    accountQueue->front = (accountQueue->front + 1 ) % accountQueue->capacity;
    accountQueue->size--;
    printf("Account Dequeued element : ");
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
    for (int i = accountQueue->front ; i < accountQueue->rear + 1 ; i++)
    {
        printf("%s\n", accountQueue->addresses[i]);
    }
}



void startGridlock()
{

}