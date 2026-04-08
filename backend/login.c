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




