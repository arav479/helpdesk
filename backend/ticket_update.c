#include<stdio.h>
#include<sqlite3.h>
#include<string.h>

int main(int argc,char *argv[]) {
    sqlite3 *db;
    char *err_msg;
    char *helptopic=argv[1];
    char *issue_summary=argv[2];
    char *problem_explaination=argv[3];
    char *location=argv[4];
    char *Department_Hostel=argv[5];
    char *mobilelenumber=argv[6];
    char *preferred_time =argv[7];
    int rc;
    rc = sqlite3_open("users.db", &db);
    if (rc != SQLITE_OK) {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
    }
    char *create_sql="CREATE TABLE IF NOT EXISTS("
    "HELPTOPIC TEXT,"
    "ISSUE_SUMMARY TEXT,"
    "PROBLEM_EXPLAINNATION TEXT,"
    "LOCATION TEXT,"
    "DEPARTMENT/HOSTEL TEXT,"
    "MOBILENUMBER TEXT,"
    "PREFERRED_TIME TEXT"
    ");";

    rc=sqlite3_exec(db,create_sql,0,0,&err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    

    
}