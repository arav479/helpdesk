#include <stdio.h>
#include <string.h>

#define MAX_LENGTH 100

int main(int argc, char *argv[])
{
    if (argc < 2)
    {
        printf("FAILURE: No action specified.\n");
        return 1;
    }

    char *action = argv[1];

    /* ======= REGISTER (existing) ======= */
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

        FILE *check_file = fopen("userdetails.txt", "r");
        if (check_file != NULL)
        {
            char fileEmail[MAX_LENGTH], filePassword[MAX_LENGTH], fileRole[MAX_LENGTH];
            while (fscanf(check_file, "%s %s %s", fileEmail, filePassword, fileRole) != EOF)
            {
                if (strcmp(email, fileEmail) == 0)
                {
                    fclose(check_file);
                    printf("FAILURE: Email already exists.\n");
                    return 1;
                }
            }
            fclose(check_file);
        }

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

    /* ======= LOGIN (existing - user/admin) ======= */
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

    /* ======================================================
       ENGINEER LOGIN (NEW)
       - Reads engineers.txt
       - Format: Department|ID|Name|Email|Password|Available
       - Matches EMAIL + PASSWORD
       - Returns: SUCCESS:engineer:Name
       ====================================================== */
    else if (strcmp(action, "engineer_login") == 0)
    {
        if (argc != 4)
        {
            printf("FAILURE: Incorrect arguments for engineer login.\n");
            return 1;
        }

        char *inputEmail = argv[2];
        char *inputPassword = argv[3];

        FILE *file = fopen("engineers.txt", "r");
        if (file == NULL)
        {
            printf("FAILURE: Engineers file not found.\n");
            return 1;
        }

        char line[300];
        while (fgets(line, sizeof(line), file))
        {
            if (strlen(line) <= 1) continue;
            line[strcspn(line, "\r\n")] = 0;

            /* Parse: Department|ID|Name|Email|Password|Available */
            char *dept = strtok(line, "|");
            char *id_str = strtok(NULL, "|");
            char *name = strtok(NULL, "|");
            char *email = strtok(NULL, "|");
            char *pass = strtok(NULL, "|");
            char *avail = strtok(NULL, "|");

            if (dept && id_str && name && email && pass)
            {
                /* Match email and password */
                if (strcmp(inputEmail, email) == 0 && strcmp(inputPassword, pass) == 0)
                {
                    fclose(file);
                    printf("SUCCESS:engineer:%s", name);
                    return 0;
                }
            }
        }
        fclose(file);
        printf("FAILURE: Invalid engineer credentials.");
        return 1;
    }

    printf("FAILURE: Unknown action.\n");
    return 1;
}
