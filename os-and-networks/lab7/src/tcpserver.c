#define _DEFAULT_SOURCE
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <port> <bufsize>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const int PORT = atoi(argv[1]);
    const int BUFSIZE = atoi(argv[2]);

    if (PORT <= 0 || PORT > 65535 || BUFSIZE <= 0) {
        fprintf(stderr, "Error: Invalid port or bufsize\n");
        exit(EXIT_FAILURE);
    }

    int server_fd, client_fd;
    struct sockaddr_in server, client;
    char buf[BUFSIZE];

    // Создание TCP сокета
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // SO_REUSEADDR для избежания "Address already in use"
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Настройка адреса сервера
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);
    server.sin_addr.s_addr = INADDR_ANY;

    // Привязка сокета
    if (bind(server_fd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("bind");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Прослушивание
    if (listen(server_fd, 5) < 0) {
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("TCP Server listening on port %d (bufsize=%d)\n", PORT, BUFSIZE);

    while (1) {
        socklen_t client_len = sizeof(client);
        
        // Принятие соединения
        client_fd = accept(server_fd, (struct sockaddr *)&client, &client_len);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client.sin_addr, client_ip, sizeof(client_ip));
        printf("Client connected: %s:%d\n", client_ip, ntohs(client.sin_port));

        // Получение данных
        ssize_t nread = recv(client_fd, buf, BUFSIZE - 1, 0);
        if (nread < 0) {
            perror("recv");
            close(client_fd);
            continue;
        }

        buf[nread] = '\0';
        printf("Received %zd bytes: %s\n", nread, buf);

        // Эхо-ответ
        if (send(client_fd, buf, nread, 0) < 0) {
            perror("send");
        }

        close(client_fd);
        printf("Client disconnected\n\n");
    }

    close(server_fd);
    return 0;
}