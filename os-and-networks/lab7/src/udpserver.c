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

    int sockfd;
    struct sockaddr_in server, client;
    char buf[BUFSIZE];

    // Создание UDP сокета
    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // Настройка адреса сервера
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);
    server.sin_addr.s_addr = INADDR_ANY;

    // Привязка сокета
    if (bind(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("bind");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("UDP Server listening on port %d (bufsize=%d)\n", PORT, BUFSIZE);

    while (1) {
        socklen_t client_len = sizeof(client);
        
        // Получение датаграммы
        ssize_t nread = recvfrom(sockfd, buf, BUFSIZE - 1, 0,
                                  (struct sockaddr *)&client, &client_len);
        if (nread < 0) {
            perror("recvfrom");
            continue;
        }

        buf[nread] = '\0';

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client.sin_addr, client_ip, sizeof(client_ip));
        printf("Received %zd bytes from %s:%d: %s\n",
               nread, client_ip, ntohs(client.sin_port), buf);

        // Эхо-ответ
        if (sendto(sockfd, buf, nread, 0,
                   (struct sockaddr *)&client, client_len) < 0) {
            perror("sendto");
        }
    }

    close(sockfd);
    return 0;
}