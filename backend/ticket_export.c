#include <stdio.h>
#include <string.h>

#define LINE_SIZE 2048
#define FIELD_COUNT 11

void write_csv_cell(FILE *out, const char *text) {
    int i;
    fputc('"', out);
    if (text != NULL) {
        for (i = 0; text[i] != '\0'; i++) {
            if (text[i] == '"') {
                fputc('"', out);
            }
            fputc(text[i], out);
        }
    }
    fputc('"', out);
}

int should_export_ticket(const char *mode, const char *filter_value, char *fields[]) {
    if (strcmp(mode, "admin") == 0) {
        return 1;
    }

    if (strcmp(mode, "user") == 0) {
        return filter_value != NULL && fields[0] != NULL && strcmp(fields[0], filter_value) == 0;
    }

    if (strcmp(mode, "engineer") == 0) {
        return filter_value != NULL && fields[9] != NULL && strcmp(fields[9], filter_value) == 0;
    }

    return 0;
}

void write_ticket_row(FILE *out, char *fields[], const char *forced_status) {
    int i;
    const char *status = forced_status != NULL ? forced_status : fields[10];

    for (i = 0; i < 10; i++) {
        write_csv_cell(out, fields[i] != NULL ? fields[i] : "");
        fputc(',', out);
    }
    write_csv_cell(out, status != NULL ? status : "Open");
    fputc('\n', out);
}

void export_file(FILE *out, const char *filename, const char *mode, const char *filter_value, const char *forced_status) {
    FILE *in = fopen(filename, "r");
    char line[LINE_SIZE];

    if (in == NULL) {
        return;
    }

    while (fgets(line, sizeof(line), in) != NULL) {
        char *fields[FIELD_COUNT] = {0};
        char *token;
        int count = 0;

        line[strcspn(line, "\r\n")] = '\0';
        if (strlen(line) == 0) {
            continue;
        }

        token = strtok(line, "|");
        while (token != NULL && count < FIELD_COUNT) {
            fields[count] = token;
            count++;
            token = strtok(NULL, "|");
        }

        if (count < 10) {
            continue;
        }

        if (should_export_ticket(mode, filter_value, fields)) {
            write_ticket_row(out, fields, forced_status);
        }
    }

    fclose(in);
}

int main(int argc, char *argv[]) {
    const char *mode;
    const char *filter_value = "";
    FILE *out;

    if (argc < 2) {
        printf("Usage: ticket_export admin | user email | engineer name\n");
        return 1;
    }

    mode = argv[1];
    if (argc >= 3) {
        filter_value = argv[2];
    }

    out = fopen("tickets_export.csv", "w");
    if (out == NULL) {
        printf("Could not create tickets_export.csv\n");
        return 1;
    }

    fprintf(out, "User Email,Ticket ID,Help Topic,Issue Summary,Detailed Explanation,Location,Department / Hostel,Mobile Number,Preferred Time,Assigned Engineer,Status\n");

    export_file(out, "ticket_credentials.txt", mode, filter_value, NULL);
    export_file(out, "deleted_tickets.txt", mode, filter_value, "Closed");

    fclose(out);
    printf("tickets_export.csv created\n");
    return 0;
}
