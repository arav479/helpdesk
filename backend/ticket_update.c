#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
int ticket_count=1;
struct ticket_details

 {
    char ticket_id[100];
    char helptopic[100];
    char issue_summary[100];
    char problem_explaination[500];
    char location[100];
    char Department_Hostel[100];
    char mobilelenumber[100];
    char preferred_time[100];
    struct ticket_details *next;

};

char *create_ticket_id(char *helptopic,char *ticket_id){

    char count=0;
    char prefix[20];
    if (strcmp(helptopic, "AC-Problem") == 0) {
        strcpy(prefix, "AC-");
    }
    else if (strcmp(helptopic, "Electrical") == 0) {
        strcpy(prefix, "EL-");
    }
    else if (strcmp(helptopic, "Network") == 0) {
        strcpy(prefix, "NW-");
    }
    else if (strcmp(helptopic, "Plumbing") == 0) {
        strcpy(prefix, "PL-");
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

    ticket_count++;
    sprintf(ticket_id, "%s%03d", prefix, ticket_count);
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
            strcpy(new_node->helptopic, token);
            create_ticket_id(new_node->helptopic, new_node->ticket_id);
            
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->issue_summary, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->problem_explaination, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->location, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->Department_Hostel, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->mobilelenumber, token);
            if ((token = strtok(NULL, "|\n"))) strcpy(new_node->preferred_time, token);
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

int main (int argc, char *argv[]) 
{
    if (argc < 8) {
        fprintf(stderr, "Usage: %s <helptopic> <issue_summary> <problem_explaination> <location> <Department_Hostel> <mobilelenumber> <preferred_time>\n", argv[0]);
        return 1;
    }
    FILE *fp;
    fp = fopen("ticket_credentials.txt", "a");
    if (fp == NULL) {
        fprintf(stderr, "Error opening ticket_credentials.txt\n");
    }
    fprintf(fp, "%s|%s|%s|%s|%s|%s|%s\n", argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7]);
    fclose(fp);
    struct ticket_details *top = extract_file_data_to_nodes();
    display_tickets(top);


}