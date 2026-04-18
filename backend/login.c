<<<<<<< HEAD
#include <stdio.h>
#include <string.h>

#define MAX_LENGTH 50

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("FAILURE: No action specified.\n");
        return 1;
    }

    char *action = argv[1];

    if (strcmp(action, "register") == 0)
    {
        if (argc != 5)
        {
            printf("FAILURE: Incorrect arguments for registration.\n");
            return 1;
        }

        char *email = argv[2];
        char *password = argv[3];
        char *role = argv[4];

        FILE *file = fopen("userdetails.txt", "a");
        if (file == NULL)
        {
            printf("FAILURE: Could not open file.\n");
            return 1;
        }

        fprintf(file, "%s %s %s\n", email, password, role);
        fclose(file);

        printf("SUCCESS");
        return 0;
    }

    else if (strcmp(action, "login") == 0)
    {
        if (argc != 4)
        {
            printf("FAILURE: Incorrect arguments for login.\n");
            return 1;
        }

        char *inputEmail = argv[2];
        char *inputPassword = argv[3];

        char fileEmail[MAX_LENGTH];
        char filePassword[MAX_LENGTH];
        char fileRole[MAX_LENGTH];

        FILE *file = fopen("userdetails.txt", "r");
        if (file == NULL)
        {
            printf("FAILURE: No users registered.\n");
            return 1;
        }

        while (fscanf(file, "%s %s %s", fileEmail, filePassword, fileRole) != EOF)
        {
            if (strcmp(inputEmail, fileEmail) == 0 && strcmp(inputPassword, filePassword) == 0)
            {
                fclose(file);
                printf("SUCCESS:%s", fileRole);
                return 0;
            }
        }

        fclose(file);
        printf("FAILURE: Invalid credentials.");
        return 1;
    }

    printf("FAILURE: Unknown action.\n");
    return 1;
}
=======
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<sqlite3.h>
#include<openssl/sha.h>
void hash_password() {
    
}

int main(int argc, char *argv[]) {
    sqlite3 *db;
    char *err_msg = 0;
    int rc;

    if (argc < 4) {
        fprintf(stderr, "Usage: %s <email> <password>\n", argv[0]);
        return 1;
    }

    char *email = argv[1];
    char *password = argv[2];
    char *role =argv[3];

    rc = sqlite3_open("users.db", &db);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
        return 1;
    }

    // Create table
    char *create_sql = "CREATE TABLE IF NOT EXISTS users ("
                       "email TEXT PRIMARY KEY, "
                       "password TEXT,"
                       "role TEXT"
                       ");";

    rc = sqlite3_exec(db, create_sql, 0, 0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "SQL error: %s\n", err_msg);
        sqlite3_free(err_msg);
    }

    // Insert user
    char sql[512];
    sprintf(sql, "INSERT OR REPLACE INTO users VALUES('%s','%s','%s');", email, password,role);

    rc = sqlite3_exec(db, sql, 0, 0, &err_msg);

    if (rc != SQLITE_OK) {
        fprintf(stderr, "Insert error: %s\n", err_msg);
        sqlite3_free(err_msg);
    } else {
        printf("User %s registered successfully!\n", email);
    }

    sqlite3_close(db);
    return 0;
}




>>>>>>> 01abd88acfb3e69120a35dc32580a7190aa35a7c
