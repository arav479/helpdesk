#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
//this is the structure of the ticket
#define TABLE_SIZE 50
struct ticket_details
 {
    char username[150];
    char ticket_id[100];
    char helptopic[100];
    char issue_summary[100];
    char problem_explaination[500];
    char location[100];
    char Department_Hostel[100];
    char mobilelenumber[100];
    char preferred_time[100];
    char assigned_engineer[100];
    struct ticket_details *next;
};
//structure to group tickets by user
struct usernode{
    char username[100];
    struct ticket_details *tickets_head;
    struct usernode *next;
};
int get_ticket_count() {
    int count = 100;
    FILE *fp = fopen("count.txt", "r");
    if (fp != NULL) {
        fscanf(fp, "%d", &count);
        fclose(fp);
    }
    return count;
}

void save_ticket_count(int count) {
    FILE *fp = fopen("count.txt", "w");
    if (fp != NULL) {
        fprintf(fp, "%d", count);
        fclose(fp);
    }
}
//LINKED LIST START
struct ticket_details *find_ticket_id_node(struct ticket_details **head,char *ticket_id) {
    struct ticket_details *temp = *head;
    while (temp != NULL) {
        if (strcmp(temp->ticket_id, ticket_id) == 0) {
            return temp;
        }
    }
}

// --- STACK DATA STRUCTURE ---
struct StackNode {
    char ticket_line[1024];
    struct StackNode* next;
};

struct Stack {
    struct StackNode* top;
};

void initStack(struct Stack* s) {
    s->top = NULL;
}

void push(struct Stack* s, char* line) {
    struct StackNode* newNode = (struct StackNode*)malloc(sizeof(struct StackNode));
    if (newNode) {
        strcpy(newNode->ticket_line, line);
        newNode->next = s->top;
        s->top = newNode;
    }
}

char* pop(struct Stack* s) {
    if (s->top == NULL) return NULL;
    struct StackNode* temp = s->top;
    char* data = (char*)malloc(1024);
    strcpy(data, temp->ticket_line);
    s->top = s->top->next;
    free(temp);
    return data;
}

void push_to_stack_file(struct ticket_details *ticket) {
    FILE *fp = fopen("deleted_tickets.txt", "a");
    if (fp != NULL) {
        fprintf(fp, "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n",
                ticket->username, ticket->ticket_id, ticket->helptopic, ticket->issue_summary,
                ticket->problem_explaination, ticket->location, ticket->Department_Hostel,
                ticket->mobilelenumber, ticket->preferred_time, ticket->assigned_engineer);
        fclose(fp);
    }
}

void delete_ticket_node_by_id(struct ticket_details **head, char *ticket_id) {
    struct ticket_details *temp = *head;
    struct ticket_details *prev = NULL;

    if (temp == NULL) {
        printf("No tickets to delete.\n");
        return;
    }

    // If head node itself holds the ticket_id to be deleted
    if (temp != NULL && strcmp(temp->ticket_id, ticket_id) == 0) {
        push_to_stack_file(temp);
        *head = temp->next;
        free(temp);
        printf("Ticket %s deleted successfully.\n", ticket_id);
        return;
    }

    // Search for the ticket_id to be deleted, keep track of the
    // previous node as we need to change 'prev->next'
    while (temp != NULL && strcmp(temp->ticket_id, ticket_id) != 0) {
        prev = temp;
        temp = temp->next;
    }

    // If ticket_id was not present in linked list
    if (temp == NULL) {
        printf("Ticket %s not found.\n", ticket_id);
        return;
    }
    push_to_stack_file(temp);
    prev->next=temp->next;
    free(temp);
    printf("Ticket %s deleted successfully.\n", ticket_id);
}

void save_nodes_to_file(struct ticket_details *head) {
    FILE *fp = fopen("ticket_credentials.txt", "w");
    if (fp == NULL) {
        fprintf(stderr, "Error opening ticket_credentials.txt for writing\n");
        return;
    }

    struct ticket_details *temp = head;
    while (temp != NULL) {
        fprintf(fp, "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n",
            temp->username,
            temp->ticket_id,temp->helptopic, temp->issue_summary,
                temp->problem_explaination, temp->location,
                temp->Department_Hostel, temp->mobilelenumber, temp->preferred_time, temp->assigned_engineer);
        temp = temp->next;
    }
    fclose(fp);
}

char *create_ticket_id(char *helptopic, char *ticket_id) {
    char prefix[20];

    // Assign prefix based on help topic to create unique ticket id
    //The count is incremented for each ticket even for all the helptopics
    //there is no unique incrementation for differenet helptopic
    if (strcmp(helptopic, "AC-Problem") == 0) {
        strcpy(prefix, "AC-");
    }
    else if (strcmp(helptopic, "Electrical") == 0) {
        strcpy(prefix, "EL-");
    }

    else if (strcmp(helptopic, "Network") == 0 || strcmp(helptopic, "Wifi-LAN Internet") == 0) {
        strcpy(prefix, "NW-");
    }
    else if (strcmp(helptopic, "Plumbing") == 0) {
        strcpy(prefix, "PL-");
    }

    else if (strcmp(helptopic, "Attendance System") == 0) {
        strcpy(prefix, "AT-");
    }
    else if (strcmp(helptopic, "Hardware") == 0) {
        strcpy(prefix, "HW-");
    }
    else if (strcmp(helptopic, "Security") == 0) {
        strcpy(prefix, "SEC-");
    }
    else {
        strcpy(prefix, "OT-");
    }

    int count = get_ticket_count();
    count++;
    sprintf(ticket_id, "%s%03d", prefix, count);
    save_ticket_count(count);
    return ticket_id;
}



void display_tickets(struct ticket_details *head)
 {
    if (head == NULL) {
        printf("No tickets available.\n");
        return;
    }

    struct ticket_details *temp = head;

    while (temp != NULL) {

        printf("----- Ticket -----\n");
        printf("User name       :%s\n",temp->username);
        printf("Ticket_id    : %s\n", temp->ticket_id);
        printf("Help Topic       : %s\n", temp->helptopic);
        printf("Issue Summary    : %s\n", temp->issue_summary);
        printf("Problem Explain  : %s\n", temp->problem_explaination);
        printf("Location         : %s\n", temp->location);
        printf("Department/Hostel: %s\n", temp->Department_Hostel);
        printf("Mobile Number    : %s\n", temp->mobilelenumber);
        printf("Preferred Time   : %s\n", temp->preferred_time);
        printf("-------------------\n\n");

        temp = temp->next;
    }
}

struct ticket_details* extract_file_data_to_nodes()
//The data of each ticket is stored in file from the main function to make  the operations converting them to linkedlist
{
    FILE *fp = fopen("ticket_credentials.txt", "r");
    if (fp == NULL) {
        fprintf(stderr, "Error opening ticket_credentials.txt\n");
        return NULL;
    }

    struct ticket_details *head = NULL, *tail = NULL;
    char line[1024];

    while (fgets(line, sizeof(line), fp)) {
        if (strlen(line) <= 1) continue;

        struct ticket_details *new_node = (struct ticket_details *)malloc(sizeof(struct ticket_details));
        if (new_node == NULL) break;
        new_node->next = NULL;

        char *token = strtok(line, "|\n");
        if (token) {
            strcpy(new_node->username, token);
            //creating the nodes with these members
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->ticket_id, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->helptopic, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->issue_summary, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->problem_explaination, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->location, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->Department_Hostel, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->mobilelenumber, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->preferred_time, token);
            if((token =strtok(NULL, "|\n"))) strcpy(new_node->assigned_engineer, token);
        }

        if (head == NULL) {
            head = new_node;
            tail = new_node;
        } else {
            tail->next = new_node;
            tail = new_node;
        }
    }

    fclose(fp);
    return head;
}

void list_tickets_parsable(struct ticket_details *head)
{
    //since we need to send the data to python in a parsable format we used
    //this function this will send to fetchticketsfunction in python
    struct ticket_details *temp = head;
    while (temp != NULL) {
        printf("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n", temp->username,
               temp->ticket_id, temp->helptopic, temp->issue_summary,
               temp->problem_explaination, temp->location,
               temp->Department_Hostel, temp->mobilelenumber, temp->preferred_time, temp->assigned_engineer);
        temp = temp->next;
    }
}
//LINKED LIST END

//HASHTABLE START
struct usernode *hash_table[TABLE_SIZE]={NULL};

// Simple Hash Function (DJB2) 
unsigned int hash_function(char *username) {
    unsigned int hash = 5381;
    int c;
    while ((c = *username++))
        hash = ((hash << 5) + hash) + c; 
    return hash % TABLE_SIZE;
}
// Function to insert a ticket into the Hash Table
void insert_into_hash_table(struct ticket_details *ticket) {
    unsigned int index = hash_function(ticket->username);
    
    // Check if user already exists in this bucket
    struct usernode *curr_user = hash_table[index];
    while (curr_user != NULL) {
        if (strcmp(curr_user->username, ticket->username) == 0) {
            // User found, add ticket to their list
            ticket->next = curr_user->tickets_head;
            curr_user->tickets_head = ticket;
            return;
        }
        curr_user = curr_user->next;
    }
    // User not found, create a new UserNode
    struct usernode *new_user = (struct usernode *)malloc(sizeof(struct usernode));
    strcpy(new_user->username, ticket->username);
    new_user->tickets_head = ticket;
    ticket->next = NULL; // This is the first ticket for this new user node
    
    // Add usernode to the hash table bucket (chaining)
    new_user->next = hash_table[index];
    hash_table[index] = new_user;
}

// Function to display tickets for a specific user
void display_user_tickets(char *username) {
    unsigned int index = hash_function(username);
    struct usernode *curr_user = hash_table[index];
    
    while (curr_user != NULL) {
        if (strcmp(curr_user->username, username) == 0) {
            list_tickets_parsable(curr_user->tickets_head);
            return;
        }
        curr_user = curr_user->next;
    }
}
//HASHTABLE END

// --- QUEUE STRUCTURES ---
struct Engineer {
    char name[100];
    char department[100];
    struct Engineer *next;
};

struct Queue {
    struct Engineer *front;
    struct Engineer *rear;
};

void initQueue(struct Queue *q) {
    q->front = NULL;
    q->rear = NULL;
}

void enqueue(struct Queue *q, char *name, char *department) {
    struct Engineer *new_eng = (struct Engineer *)malloc(sizeof(struct Engineer));
    strcpy(new_eng->name, name);
    strcpy(new_eng->department, department);
    new_eng->next = NULL;
    if (q->rear == NULL) {
        q->front = q->rear = new_eng;
        return;
    }
    q->rear->next = new_eng;
    q->rear = new_eng;
}

struct Engineer* dequeue(struct Queue *q) {
    if (q->front == NULL) return NULL;
    struct Engineer *temp = q->front;
    q->front = q->front->next;
    if (q->front == NULL) q->rear = NULL;
    return temp;
}

// --- SMART ASSIGNMENT LOGIC ---
void assign_engineer(char *helptopic, char *assigned_name) {
    FILE *fp = fopen("engineers.txt", "r");
    if (fp == NULL) {
        strcpy(assigned_name, "Unassigned");
        return;
    }

    struct Queue dept_queue;
    initQueue(&dept_queue);
    struct Queue other_queue;
    initQueue(&other_queue);

    char line[200];
    // 1. Read file, map departments, build queues
    while (fgets(line, sizeof(line), fp)) {
        if (strlen(line) <= 1) continue;
        line[strcspn(line, "\r\n")] = 0; // Remove newline
        
        char *dept = strtok(line, "|");
        char *name = strtok(NULL, "");
        
        if (dept && name) {
            if (strcmp(dept, helptopic) == 0) {
                enqueue(&dept_queue, name, dept);
            } else {
                enqueue(&other_queue, name, dept);
            }
        }
    }
    fclose(fp);

    // 2. Round-Robin Assignment
    if (dept_queue.front != NULL) {
        struct Engineer *assigned_eng = dequeue(&dept_queue);
        strcpy(assigned_name, assigned_eng->name);
        // Move engineer to the back of the queue
        enqueue(&dept_queue, assigned_eng->name, assigned_eng->department);
        free(assigned_eng);
    } else {
        strcpy(assigned_name, "Unassigned");
    }

    // 3. Save the rotated queues back to the file
    fp = fopen("engineers.txt", "w");
    if (fp != NULL) {
        struct Engineer *temp;
        while ((temp = dequeue(&dept_queue)) != NULL) {
            fprintf(fp, "%s|%s\n", temp->department, temp->name);
            free(temp);
        }
        while ((temp = dequeue(&other_queue)) != NULL) {
            fprintf(fp, "%s|%s\n", temp->department, temp->name);
            free(temp);
        }
        fclose(fp);
    }
}

int main (int argc, char *argv[])
{
    if (argc == 2 && strcmp(argv[1], "undo") == 0) {
        FILE *fp_stack = fopen("deleted_tickets.txt", "r");
        if (fp_stack == NULL) {
            printf("Nothing to undo.\n");
            return 0;
        }

        struct Stack s;
        initStack(&s);
        char line[1024];

        // 1. Read file and PUSH onto stack
        while (fgets(line, sizeof(line), fp_stack)) {
            push(&s, line);
        }
        fclose(fp_stack);

        // 2. POP the last deleted ticket
        char* restored_ticket = pop(&s);
        
        if (restored_ticket == NULL) {
            printf("Nothing to undo.\n");
            return 0;
        }

        // 3. Restore to database
        FILE *fp_tickets = fopen("ticket_credentials.txt", "a");
        if (fp_tickets != NULL) {
            fprintf(fp_tickets, "%s", restored_ticket);
            fclose(fp_tickets);
        }
        free(restored_ticket);

        // 4. Save remaining stack back to file (Reverse order to maintain stack)
        // Note: Since pop() gave us the top, we need to get the rest of the items
        // In a real app, we'd rebuild the file from the remaining stack.
        fp_stack = fopen("deleted_tickets.txt", "w");
        if (fp_stack != NULL) {
            struct Stack tempStack;
            initStack(&tempStack);
            
            // Move to temp stack to reverse order for correct file writing
            char* moveLine;
            while ((moveLine = pop(&s)) != NULL) {
                push(&tempStack, moveLine);
                free(moveLine);
            }
            
            while ((moveLine = pop(&tempStack)) != NULL) {
                fprintf(fp_stack, "%s", moveLine);
                free(moveLine);
            }
            fclose(fp_stack);
        }
        
        printf("Undo successful.\n");
        return 0;
    }

    if (argc == 2 && strcmp(argv[1], "list") == 0) {
        //fetch ticket
            struct ticket_details *top = extract_file_data_to_nodes();
            list_tickets_parsable(top);
            return 0;
        }
    if (argc == 3 && strcmp(argv[1], "delete") == 0 ) {
        //delete ticket
            struct ticket_details *top = extract_file_data_to_nodes();
            delete_ticket_node_by_id(&top, argv[2]);
            save_nodes_to_file(top);
            return 0;
        }
    if (argc == 3 && strcmp(argv[1], "viewmytickets") == 0 ) {
        //load the tickets of the specific user
        struct ticket_details *top = extract_file_data_to_nodes();
        // Use hash table to display tickets for a specific user
        struct ticket_details *temp = top;
        while (temp != NULL) {
            struct ticket_details *next_node = temp->next;
            insert_into_hash_table(temp);
            temp = next_node;
        }   
        display_user_tickets(argv[2]);  
    return 0;        
    }

    if (argc < 9) {
        fprintf(stderr, "Usage: %s<username> <ticket_id> <helptopic> <issue_summary> <problem_explaination> <location> <Department_Hostel> <mobilelenumber> <preferred_time>\n", argv[0]);
        return 1;
    }
    FILE *fp;
    fp = fopen("ticket_credentials.txt", "a");
    if (fp == NULL){
        fprintf(stderr, "Error opening ticket_credentials.txt\n");
        return 1;
    }
    char ticket_id[100];
    create_ticket_id(argv[1], ticket_id);

    char assigned_engineer_name[100];
    assign_engineer(argv[1], assigned_engineer_name); 
    fprintf(fp, "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n", 
            argv[8], ticket_id, argv[1], argv[2], argv[3], 
            argv[4], argv[5], argv[6], argv[7], assigned_engineer_name);
    fclose(fp);
    
}
