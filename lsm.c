
#include <stdio.h>
#include <stdlib.h>  
#include <string.h>
#include <inttypes.h>



#define MAX_ACCOUNTS 10
#define MAX_ADDRESS_SIZE 256
#define MAX_QUEUE_CAPACITY 100

// Structures 


typedef struct Account {
    char address[MAX_ADDRESS_SIZE];
    int balance;
    int netBalance; // Net balance used during GridLock Resolution
} Account;

typedef struct OffsetTx {
    uint64_t id;
    char senderAddress[MAX_ADDRESS_SIZE];
    char receiverAddress[MAX_ADDRESS_SIZE];
    int amount;
} OffsetTx;

typedef struct Queue {
    int front, rear, size;
    int capacity;
    OffsetTx *transactions;
} Queue;

// Prototypes

    // Accounts prototypes
static void initAccounts();
static Account createAccount(char* address, int balance, int netBalance);
void printAccounts();

    // OffsetTx prototypes
static OffsetTx createOffsetTx(char *senderAddress, char *receiverAddress, int amount);
void printOffsetTx(OffsetTx tx);

    // Queues prototypes
static void initQueue(int capacity);
void enqueue(OffsetTx tx);
OffsetTx *dequeue();
int isFull();
int isEmpty();
OffsetTx *getRear();
OffsetTx *getFront();
void printQueue();

// Global variables
Account *accounts;
int accountsLength;
Queue *queue;

int main()
{
    initAccounts();
    printAccounts();
    initQueue(MAX_QUEUE_CAPACITY);

    // Queue test
    dequeue();
    printQueue();
    enqueue(createOffsetTx("0x1234", "0x5678", 2000));
    enqueue(createOffsetTx("0x5678", "0x1234", 2500));
    enqueue(createOffsetTx("0x8888", "0x5678", 4000));
    enqueue(createOffsetTx("0x9999", "0x5678", 4500));
    getRear();
    getFront();
    dequeue();
    dequeue();
    printQueue();


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


static OffsetTx createOffsetTx(char *senderAddress, char *receiverAddress, int amount)
{
    //if (amount <= 0 ) return NULL;
    OffsetTx tx;
    // TODO Generate TXID
    tx.id = 0;
    strcpy(tx.receiverAddress, receiverAddress);
    strcpy(tx.senderAddress, senderAddress);
    tx.amount  = amount;
    return tx;
}

void printOffsetTx(OffsetTx tx)
{
    printf("%lu, %s, %s, %d \n", tx.id, tx.senderAddress, tx.receiverAddress, tx.amount);
}

static void initQueue(int capacity){
    queue = malloc(sizeof(Queue));
    queue->capacity = capacity;
    queue->size = 0;
    queue->rear = capacity - 1;
    queue->front = 0;
    queue->size = 0;
    queue->transactions = (OffsetTx*) malloc(sizeof(capacity * sizeof(OffsetTx)));
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
    return (queue->size == 0);
}

OffsetTx *getRear(){
    if(isEmpty()) return NULL;
    OffsetTx *tx =  & (queue->transactions[queue->rear]);
    printf("Rear element : %lu, %s, %s, %d \n", tx->id, tx->senderAddress, tx->receiverAddress, tx->amount);
    return tx;
   
}
OffsetTx *getFront(){
    if(isEmpty()) return NULL;
    OffsetTx *tx =  &(queue->transactions[queue->front]);
    printf("Front element : %lu, %s, %s, %d \n", tx->id, tx->senderAddress, tx->receiverAddress, tx->amount);
    return tx;
}

void printQueue(){
    if (isEmpty()) {printf("The queue is empty.\n");return;}
    for (int i = queue->front ; i < queue->rear + 1 ; i++)
    {
        printOffsetTx( (queue->transactions)[i] );
    }
}