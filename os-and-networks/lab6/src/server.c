#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <signal.h>
#include <endian.h>
#include "protocol.h"

volatile sig_atomic_t keep_running = 1;

void sigint_handler(int sig) {
    (void)sig;
    keep_running = 0;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <port>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    int port = atoi(argv[1]);
    if (port <= 0 || port > 65535) {
        fprintf(stderr, "Error: Invalid port number\n");
        exit(EXIT_FAILURE);
    }

    signal(SIGINT, sigint_handler);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 10) < 0) {
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Server listening on port %d\n", port);

    while (keep_running) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);

        int client_fd = accept(server_fd, (struct sockaddr *)&client_addr, &client_len);
        if (client_fd < 0) {
            if (!keep_running) break;
            perror("accept");
            continue;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, client_ip, sizeof(client_ip));
        printf("Client connected: %s:%d\n", client_ip, ntohs(client_addr.sin_port));

        Task task;
        ssize_t bytes_received = recv(client_fd, &task, sizeof(Task), 0);
        if (bytes_received != sizeof(Task)) {
            fprintf(stderr, "Error: Failed to receive task\n");
            close(client_fd);
            continue;
        }

        // Преобразование из network byte order
        task.start = be64toh(task.start);
        task.end = be64toh(task.end);
        task.mod = be64toh(task.mod);

        printf("Task received: calculate product from %lu to %lu mod %lu\n",
               task.start, task.end, task.mod);

        uint64_t result = calculate_partial(task.start, task.end, task.mod);
        printf("Calculated result: %lu\n", result);

        Response response;
        response.result = htobe64(result);

        ssize_t bytes_sent = send(client_fd, &response, sizeof(Response), 0);
        if (bytes_sent != sizeof(Response)) {
            fprintf(stderr, "Error: Failed to send response\n");
        }

        close(client_fd);
        printf("Client disconnected\n\n");
    }

    close(server_fd);
    printf("Server shutdown\n");

    return 0;
}