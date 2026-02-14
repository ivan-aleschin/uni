#define _DEFAULT_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <stdbool.h>
#include <endian.h>
#include <sys/time.h>
#include "protocol.h"

#define MAX_SERVERS 256
#define BUFFER_SIZE 256
#define RECV_TIMEOUT_SEC 5

typedef struct {
    char ip[INET_ADDRSTRLEN];
    int port;
} Server;

typedef struct {
    Server server;
    Task task;
    uint64_t partial_result;
    bool success;
} ThreadData;

pthread_mutex_t result_mutex = PTHREAD_MUTEX_INITIALIZER;
uint64_t global_result = 1;

void* server_worker(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    data->success = false;

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return NULL;
    }

    // Установка таймаута для recv
    struct timeval timeout;
    timeout.tv_sec = RECV_TIMEOUT_SEC;
    timeout.tv_usec = 0;
    
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
        perror("setsockopt (recv timeout)");
    }

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(data->server.port);

    if (inet_pton(AF_INET, data->server.ip, &server_addr.sin_addr) <= 0) {
        fprintf(stderr, "Error: Invalid address for %s:%d\n",
                data->server.ip, data->server.port);
        close(sockfd);
        return NULL;
    }

    printf("Connecting to %s:%d...\n", data->server.ip, data->server.port);
    if (connect(sockfd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        close(sockfd);
        return NULL;
    }
    printf("Connected to %s:%d\n", data->server.ip, data->server.port);

    Task task_network;
    task_network.start = htobe64(data->task.start);
    task_network.end = htobe64(data->task.end);
    task_network.mod = htobe64(data->task.mod);

    ssize_t bytes_sent = send(sockfd, &task_network, sizeof(Task), 0);
    if (bytes_sent != sizeof(Task)) {
        fprintf(stderr, "Error: Failed to send task to %s:%d\n",
                data->server.ip, data->server.port);
        close(sockfd);
        return NULL;
    }

    printf("Sent task to %s:%d: range [%lu, %lu] mod %lu\n",
           data->server.ip, data->server.port,
           data->task.start, data->task.end, data->task.mod);

    Response response;
    ssize_t bytes_received = recv(sockfd, &response, sizeof(Response), 0);
    if (bytes_received != sizeof(Response)) {
        if (bytes_received == 0) {
            fprintf(stderr, "Error: Connection closed by %s:%d\n",
                    data->server.ip, data->server.port);
        } else if (bytes_received < 0) {
            fprintf(stderr, "Error: Timeout or recv error from %s:%d\n",
                    data->server.ip, data->server.port);
        } else {
            fprintf(stderr, "Error: Incomplete response from %s:%d (got %zd bytes, expected %zu)\n",
                    data->server.ip, data->server.port, bytes_received, sizeof(Response));
        }
        close(sockfd);
        return NULL;
    }

    data->partial_result = be64toh(response.result);
    printf("Received result from %s:%d: %lu\n",
           data->server.ip, data->server.port, data->partial_result);

    pthread_mutex_lock(&result_mutex);
    global_result = (global_result * data->partial_result) % data->task.mod;
    pthread_mutex_unlock(&result_mutex);

    close(sockfd);
    data->success = true;

    return NULL;
}

int read_servers(const char* filename, Server* servers, int max_servers) {
    FILE* file = fopen(filename, "r");
    if (!file) {
        perror("fopen");
        return -1;
    }

    int count = 0;
    char line[BUFFER_SIZE];

    while (fgets(line, sizeof(line), file) && count < max_servers) {
        line[strcspn(line, "\n")] = 0;

        if (strlen(line) == 0 || line[0] == '#') {
            continue;
        }

        char ip_temp[BUFFER_SIZE];
        int port_temp;
        
        if (sscanf(line, "%255[^:]:%d", ip_temp, &port_temp) != 2) {
            fprintf(stderr, "Warning: Invalid format in line: %s\n", line);
            continue;
        }

        if (strlen(ip_temp) >= INET_ADDRSTRLEN) {
            fprintf(stderr, "Warning: IP address too long: %s\n", ip_temp);
            continue;
        }

        if (port_temp <= 0 || port_temp > 65535) {
            fprintf(stderr, "Warning: Invalid port %d\n", port_temp);
            continue;
        }

        strcpy(servers[count].ip, ip_temp);
        servers[count].port = port_temp;
        count++;
    }

    fclose(file);
    return count;
}

int main(int argc, char *argv[]) {
    if (argc != 7) {
        fprintf(stderr, "Usage: %s -k <number> -m <mod> --servers <file>\n", argv[0]);
        fprintf(stderr, "Example: %s -k 10 -m 1000 --servers servers.txt\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    uint64_t k = 0;
    uint64_t mod = 0;
    char* servers_file = NULL;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-k") == 0 && i + 1 < argc) {
            k = strtoull(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "-m") == 0 && i + 1 < argc) {
            mod = strtoull(argv[++i], NULL, 10);
        } else if (strcmp(argv[i], "--servers") == 0 && i + 1 < argc) {
            servers_file = argv[++i];
        }
    }

    if (k == 0 || mod == 0 || !servers_file) {
        fprintf(stderr, "Error: All parameters (-k, -m, --servers) are required\n");
        exit(EXIT_FAILURE);
    }

    printf("Computing %lu! mod %lu\n", k, mod);

    Server servers[MAX_SERVERS];
    int num_servers = read_servers(servers_file, servers, MAX_SERVERS);

    if (num_servers <= 0) {
        fprintf(stderr, "Error: No valid servers found in %s\n", servers_file);
        exit(EXIT_FAILURE);
    }

    printf("Found %d server(s)\n", num_servers);

    pthread_t threads[num_servers];
    ThreadData thread_data[num_servers];

    uint64_t range = k / num_servers;
    uint64_t remainder = k % num_servers;
    uint64_t start = 1;

    for (int i = 0; i < num_servers; i++) {
        thread_data[i].server = servers[i];
        thread_data[i].task.start = start;
        thread_data[i].task.end = start + range - 1;

        if (i == num_servers - 1) {
            thread_data[i].task.end += remainder;
        }

        thread_data[i].task.mod = mod;
        thread_data[i].partial_result = 0;
        thread_data[i].success = false;

        printf("Server %d (%s:%d): will calculate range [%lu, %lu]\n",
               i, servers[i].ip, servers[i].port,
               thread_data[i].task.start, thread_data[i].task.end);

        if (pthread_create(&threads[i], NULL, server_worker, &thread_data[i]) != 0) {
            perror("pthread_create");
            exit(EXIT_FAILURE);
        }

        start = thread_data[i].task.end + 1;
    }

    int successful_threads = 0;
    for (int i = 0; i < num_servers; i++) {
        pthread_join(threads[i], NULL);

        if (thread_data[i].success) {
            printf("Thread %d completed: partial result = %lu\n",
                   i, thread_data[i].partial_result);
            successful_threads++;
        } else {
            fprintf(stderr, "Thread %d failed\n", i);
        }
    }

    printf("\n=== Final Result ===\n");
    if (successful_threads == num_servers) {
        printf("%lu! mod %lu = %lu\n", k, mod, global_result);
    } else {
        fprintf(stderr, "Warning: Only %d/%d servers completed successfully\n", 
                successful_threads, num_servers);
        fprintf(stderr, "Partial result: %lu! mod %lu = %lu\n", k, mod, global_result);
    }

    pthread_mutex_destroy(&result_mutex);

    return 0;
}