#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

struct ticket_details
 {
    char helptopic[100];
    char issue_summary[100];
    char problem_explaination[500];
    char location[100];
    char Department_Hostel[100];
    char mobilelenumber[100];
    char preferred_time[100];
    struct ticket_details *next;

};
void display_tickets(struct ticket_details *head)
 {
    if (head == NULL) {
        printf("No tickets available.\n");
        return;
    }

    struct ticket_details *temp = head;

    while (temp != NULL) {

        printf("----- Ticket -----\n");
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
    struct ticket_details *ticket_node;
    struct ticket_details *list_ptr;
    struct ticket_details  *temp;
    FILE *fp;
    fp = fopen("ticket_credentials.txt", "r");
    if (fp == NULL) {
        fprintf(stderr, "Error opening ticket_credentials.txt\n");
        return NULL;
    }
    int i=0,count=1;
    char text[100];
    ticket_node = (struct ticket_details *)malloc(sizeof(struct ticket_details));
    list_ptr=ticket_node;
    temp=ticket_node;
    ticket_node->next=NULL;

    char ch;
    while ((ch = fgetc(fp)) != EOF) {

        if (ch!='|'  && ch!='\n') {
            if (i<99) {
                text[i++]=ch;
            }

        }
        if (ch=='|'||ch=='\n') {
            text[i]='\0';
            i=0;
            count++;
        }

        if (count == 1) {
            strcpy(ticket_node->helptopic,text);
        }
        else if (count == 2) {
            strcpy(ticket_node->issue_summary,text);
        }
        else if (count == 3) {
            strcpy(ticket_node->problem_explaination,text);
        }
        else if (count == 4) {
            strcpy(ticket_node->location,text);
        }
        else if (count == 5) {
            strcpy(ticket_node->Department_Hostel,text);
        }
        else if (count == 6) {
            strcpy(ticket_node->mobilelenumber,text);
        }
        else if (count == 7) {
            strcpy(ticket_node->preferred_time,text);
        }
        else {
            text[i++]=ch;
        }
        if (ch=='\n') {
            count=1;
            ticket_node=(struct ticket_details *)malloc(sizeof(struct ticket_details));
            temp->next=ticket_node;
            ticket_node->next=NULL;
            temp=temp->next;
        }
    }
    fclose(fp);
    return list_ptr;
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
    fprintf(fp, "%s|%s|%s|%s|%s|%s|%s", argv[1], argv[2], argv[3], argv[4], argv[5], argv[6], argv[7]);
    fclose(fp);
    struct ticket_details *top = extract_file_data_to_nodes();
    display_tickets(top);
    return 0;



}