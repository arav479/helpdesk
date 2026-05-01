#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#define TABLE_SIZE 50

struct ticket_details {
    char username[150];
    char ticket_id[100];
    char helptopic[100];
    char issue_summary[100];
    char problem_explanation[500];
    char location[100];
    char Department_Hostel[100];
    char mobilelenumber[100];
    char preferred_time[100];
    char assigned_engineer[100];
    struct ticket_details *next;
};

struct usernode {
    char username[100];
    struct ticket_details *tickets_head;
    struct usernode *next;
};

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

// --- STACK FOR UNDO ---
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
    char* data = strdup(temp->ticket_line);
    s->top = s->top->next;
    free(temp);
    return data;
}

void push_to_stack_file(struct ticket_details *ticket) {
    FILE *fp = fopen("deleted_tickets.txt", "a");
    if (fp != NULL) {
        fprintf(fp, "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n",
                ticket->username, ticket->ticket_id, ticket->helptopic, ticket->issue_summary,
                ticket->problem_explanation, ticket->location, ticket->Department_Hostel,
                ticket->mobilelenumber, ticket->preferred_time, ticket->assigned_engineer);
        fclose(fp);
    }
}

void save_nodes_to_file(struct ticket_details *head) {
    FILE *fp = fopen("ticket_credentials.txt", "w");
    if (fp == NULL) return;
    struct ticket_details *temp = head;
    while (temp != NULL) {
        fprintf(fp, "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n",
                temp->username, temp->ticket_id, temp->helptopic, temp->issue_summary,
                temp->problem_explanation, temp->location, temp->Department_Hostel,
                temp->mobilelenumber, temp->preferred_time, temp->assigned_engineer);
        temp = temp->next;
    }
    fclose(fp);
}

void delete_ticket_node_by_id(struct ticket_details **head, char *ticket_id) {
    struct ticket_details *temp = *head, *prev = NULL;
    while (temp != NULL && strcmp(temp->ticket_id, ticket_id) != 0) {
        prev = temp;
        temp = temp->next;
    }
    if (temp == NULL) return;
    push_to_stack_file(temp);
    if (prev == NULL) *head = temp->next;
    else prev->next = temp->next;
    free(temp);
}

struct ticket_details* extract_file_data_to_nodes() {
    FILE *fp = fopen("ticket_credentials.txt", "r");
    if (fp == NULL) return NULL;
    struct ticket_details *head = NULL, *tail = NULL;
    char line[1024];
    while (fgets(line, sizeof(line), fp)) {
        if (strlen(line) <= 1) continue;
        struct ticket_details *new_node = (struct ticket_details *)malloc(sizeof(struct ticket_details));
        new_node->next = NULL;
        char *token = strtok(line, "|\n");
        if (token) {
            strcpy(new_node->username, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->ticket_id, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->helptopic, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->issue_summary, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->problem_explanation, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->location, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->Department_Hostel, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->mobilelenumber, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->preferred_time, token);
            if((token = strtok(NULL, "|\n"))) strcpy(new_node->assigned_engineer, token);
            else strcpy(new_node->assigned_engineer, "Unassigned");
        }
        if (head == NULL) { head = new_node; tail = new_node; }
        else { tail->next = new_node; tail = new_node; }
    }
    fclose(fp);
    return head;
}

void list_tickets_parsable(struct ticket_details *head) {
    struct ticket_details *temp = head;
    while (temp != NULL) {
        printf("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n", temp->username,
               temp->ticket_id, temp->helptopic, temp->issue_summary,
               temp->problem_explanation, temp->location,
               temp->Department_Hostel, temp->mobilelenumber, temp->preferred_time, temp->assigned_engineer);
        temp = temp->next;
    }
}

char *assign_engineer(char *helptopic, char *assigned_name) {
    FILE *fp = fopen("engineers.txt", "r");
    if (fp == NULL) { strcpy(assigned_name, "Unassigned"); return assigned_name; }
    struct Queue dept_queue, other_queue;
    initQueue(&dept_queue); initQueue(&other_queue);
    char line[200];
    while (fgets(line, sizeof(line), fp)) {
        if (strlen(line) <= 1) continue;
        line[strcspn(line, "\r\n")] = 0;
        char *dept = strtok(line, "|");
        char *name = strtok(NULL, "");
        if (dept && name) {
            if (strcmp(dept, helptopic) == 0) enqueue(&dept_queue, name, dept);
            else enqueue(&other_queue, name, dept);
        }
    }
    fclose(fp);
    if (dept_queue.front != NULL) {
        struct Engineer *assigned_eng = dequeue(&dept_queue);
        strcpy(assigned_name, assigned_eng->name);
        enqueue(&dept_queue, assigned_eng->name, assigned_eng->department);
        free(assigned_eng);
    } else { strcpy(assigned_name, "Unassigned"); }
    fp = fopen("engineers.txt", "w");
    if (fp != NULL) {
        struct Engineer *temp;
        while ((temp = dequeue(&dept_queue)) != NULL) { fprintf(fp, "%s|%s\n", temp->department, temp->name); free(temp); }
        while ((temp = dequeue(&other_queue)) != NULL) { fprintf(fp, "%s|%s\n", temp->department, temp->name); free(temp); }
        fclose(fp);
    }
    return assigned_name;
}

void close_and_reassign_ticket(char *ticket_id_to_close) {
    struct ticket_details *head = extract_file_data_to_nodes();
    if (head == NULL) return;
    struct ticket_details *temp = head, *prev = NULL, *to_close = NULL;
    while (temp != NULL) {
        if (strcmp(temp->ticket_id, ticket_id_to_close) == 0) { to_close = temp; break; }
        prev = temp; temp = temp->next;
    }
    if (to_close == NULL) return;
    char eng[100]; strcpy(eng, to_close->assigned_engineer);
    delete_ticket_node_by_id(&head, ticket_id_to_close);
    temp = head;
    while (temp != NULL) {
        if (strcmp(temp->assigned_engineer, "Unassigned") == 0) { strcpy(temp->assigned_engineer, eng); break; }
        temp = temp->next;
    }
    save_nodes_to_file(head);
}

void assign_all_unassigned_tickets() {
    struct ticket_details *head = extract_file_data_to_nodes();
    if (head == NULL) return;
    struct ticket_details *temp = head;
    while (temp != NULL) {
        if (strcmp(temp->assigned_engineer, "Unassigned") == 0) {
            char eng[100]; assign_engineer(temp->helptopic, eng);
            strcpy(temp->assigned_engineer, eng);
        }
        temp = temp->next;
    }
    save_nodes_to_file(head);
}

int main(int argc, char *argv[]) {
    if (argc == 2 && strcmp(argv[1], "undo") == 0) {
        FILE *fp_stack = fopen("deleted_tickets.txt", "r");
        if (fp_stack == NULL) return 0;
        struct Stack s; initStack(&s);
        char line[1024];
        while (fgets(line, sizeof(line), fp_stack)) {
            if (strlen(line) > 5) push(&s, line);
        }
        fclose(fp_stack);
        char* restored = pop(&s);
        if (restored == NULL) return 0;
        FILE *fp_tickets = fopen("ticket_credentials.txt", "a");
        if (fp_tickets != NULL) { fprintf(fp_tickets, "%s", restored); fclose(fp_tickets); }
        free(restored);
        fp_stack = fopen("deleted_tickets.txt", "w");
        if (fp_stack != NULL) {
            struct Stack ts; initStack(&ts);
            char* ml;
            while ((ml = pop(&s)) != NULL) { push(&ts, ml); free(ml); }
            while ((ml = pop(&ts)) != NULL) { fprintf(fp_stack, "%s", ml); free(ml); }
            fclose(fp_stack);
        }
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "list") == 0) {
        struct ticket_details *top = extract_file_data_to_nodes();
        list_tickets_parsable(top);
        return 0;
    }
    if (argc == 3 && strcmp(argv[1], "delete") == 0) {
        struct ticket_details *top = extract_file_data_to_nodes();
        delete_ticket_node_by_id(&top, argv[2]);
        save_nodes_to_file(top);
        return 0;
    }
    if (argc == 3 && strcmp(argv[1], "close") == 0) {
        close_and_reassign_ticket(argv[2]);
        return 0;
    }
    if (argc == 2 && strcmp(argv[1], "assignall") == 0) {
        assign_all_unassigned_tickets();
        return 0;
    }
    if (argc == 3 && strcmp(argv[1], "viewmytickets") == 0) {
        struct ticket_details *top = extract_file_data_to_nodes();
        struct ticket_details *temp = top;
        while (temp != NULL) {
            if (strcmp(temp->username, argv[2]) == 0) {
                printf("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n", temp->username,
                       temp->ticket_id, temp->helptopic, temp->issue_summary,
                       temp->problem_explanation, temp->location,
                       temp->Department_Hostel, temp->mobilelenumber, temp->preferred_time, temp->assigned_engineer);
            }
            temp = temp->next;
        }
        return 0;
    }
    if (argc >= 9) {
        FILE *fp = fopen("ticket_credentials.txt", "a");
        if (fp == NULL) return 1;
        char tid[100], eng[100];
        strcpy(tid, ""); // Reset
        char prefix[20] = "OT-";
        if (strcmp(argv[1], "AC-Problem") == 0) strcpy(prefix, "AC-");
        else if (strcmp(argv[1], "Electrical") == 0) strcpy(prefix, "EL-");
        else if (strcmp(argv[1], "Network") == 0) strcpy(prefix, "NW-");
        else if (strcmp(argv[1], "Plumbing") == 0) strcpy(prefix, "PL-");
        int count = get_ticket_count(); count++;
        sprintf(tid, "%s%03d", prefix, count);
        save_ticket_count(count);
        assign_engineer(argv[1], eng);
        fprintf(fp, "%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n", argv[8], tid, argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7], eng);
        fclose(fp);
    }
    return 0;
}
