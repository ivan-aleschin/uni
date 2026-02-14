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
    if (argc != 4) {
        fprintf(stderr, "Usage: %s <ip> <port> <bufsize>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    const char *IP = argv[1];
    const int PORT = atoi(argv[2]);
    const int BUFSIZE = atoi(argv[3]);

    if (PORT <= 0 || PORT > 65535 || BUFSIZE <= 0) {
        fprintf(stderr, "Error: Invalid port or bufsize\n");
        exit(EXIT_FAILURE);
    }

    int sockfd;
    struct sockaddr_in server;
    char sendline[BUFSIZE];
    char recvline[BUFSIZE];

    // Создание TCP сокета
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    // Настройка адреса сервера
    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);

    if (inet_pton(AF_INET, IP, &server.sin_addr) <= 0) {
        fprintf(stderr, "Error: Invalid IP address\n");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Подключение к серверу
    printf("Connecting to %s:%d...\n", IP, PORT);
    if (connect(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("connect");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("Connected! Enter message: ");
    if (fgets(sendline, BUFSIZE, stdin) == NULL) {
        fprintf(stderr, "Error reading input\n");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    size_t len = strlen(sendline);
    if (len > 0 && sendline[len - 1] == '\n') {
        sendline[len - 1] = '\0';
        len--;
    }

    // Отправка данных
    printf("Sending: %s\n", sendline);
    if (send(sockfd, sendline, len, 0) < 0) {
        perror("send");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    // Получение эхо-ответа
    ssize_t nread = recv(sockfd, recvline, BUFSIZE - 1, 0);
    if (nread < 0) {
        perror("recv");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    recvline[nread] = '\0';
    printf("Received: %s\n", recvline);

    close(sockfd);
    return 0;
}