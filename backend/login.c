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