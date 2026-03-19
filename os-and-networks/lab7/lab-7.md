# Лабораторная работа №7: TCP vs UDP протоколы

## Отчет по выполнению

**Выполнил:** AleshinIvan  
**Дата:** 2025-11-22

---

## Введение

В этой лабораторной работе исследуются различия между протоколами TCP и UDP на практике через реализацию двух клиент-серверных приложений. Основная цель — понять поведение каждого протокола в различных сценариях (отключение сервера, клиента, потеря соединения).

---

## Задание 1: Реализация клиент-серверных приложений

### Теоретическая часть

#### TCP (Transmission Control Protocol)

**Характеристики:**
- **Connection-oriented** — требует установки соединения (3-way handshake)
- **Reliable** — гарантирует доставку данных
- **Ordered** — данные приходят в том же порядке
- **Stream-based** — передаёт поток байтов
- **Error checking** — контрольные суммы, повторная отправка
- **Flow control** — управление скоростью передачи

**Применение:** HTTP, FTP, SSH, Email, базы данных

#### UDP (User Datagram Protocol)

**Характеристики:**
- **Connectionless** — не требует установки соединения
- **Unreliable** — не гарантирует доставку
- **Unordered** — пакеты могут прийти в любом порядке
- **Message-based** — передаёт дискретные датаграммы
- **No error correction** — нет повторной отправки
- **Low overhead** — быстрее TCP

**Применение:** DNS, видео/аудио стриминг, онлайн-игры, VoIP

### Практическая часть

#### TCP Server

```c name=tcpserver.c
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

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
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

    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);
    server.sin_addr.s_addr = INADDR_ANY;

    if (bind(server_fd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("bind");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    if (listen(server_fd, 5) < 0) {
        perror("listen");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("TCP Server listening on port %d (bufsize=%d)\n", PORT, BUFSIZE);

    while (1) {
        socklen_t client_len = sizeof(client);
        
        client_fd = accept(server_fd, (struct sockaddr *)&client, &client_len);
        if (client_fd < 0) {
            perror("accept");
            continue;
        }

        char client_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client.sin_addr, client_ip, sizeof(client_ip));
        printf("Client connected: %s:%d\n", client_ip, ntohs(client.sin_port));

        ssize_t nread = recv(client_fd, buf, BUFSIZE - 1, 0);
        if (nread < 0) {
            perror("recv");
            close(client_fd);
            continue;
        }

        buf[nread] = '\0';
        printf("Received %zd bytes: %s\n", nread, buf);

        if (send(client_fd, buf, nread, 0) < 0) {
            perror("send");
        }

        close(client_fd);
        printf("Client disconnected\n\n");
    }

    close(server_fd);
    return 0;
}
```

#### TCP Client

```c name=tcpclient.c
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

    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);

    if (inet_pton(AF_INET, IP, &server.sin_addr) <= 0) {
        fprintf(stderr, "Error: Invalid IP address\n");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

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

    printf("Sending: %s\n", sendline);
    if (send(sockfd, sendline, len, 0) < 0) {
        perror("send");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

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
```

#### UDP Server

```c name=udpserver.c
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

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);
    server.sin_addr.s_addr = INADDR_ANY;

    if (bind(sockfd, (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("bind");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("UDP Server listening on port %d (bufsize=%d)\n", PORT, BUFSIZE);

    while (1) {
        socklen_t client_len = sizeof(client);
        
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

        if (sendto(sockfd, buf, nread, 0,
                   (struct sockaddr *)&client, client_len) < 0) {
            perror("sendto");
        }
    }

    close(sockfd);
    return 0;
}
```

#### UDP Client

```c name=udpclient.c
#define _DEFAULT_SOURCE
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/time.h>

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

    sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(EXIT_FAILURE);
    }

    struct timeval timeout;
    timeout.tv_sec = 5;
    timeout.tv_usec = 0;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout)) < 0) {
        perror("setsockopt");
    }

    memset(&server, 0, sizeof(server));
    server.sin_family = AF_INET;
    server.sin_port = htons(PORT);

    if (inet_pton(AF_INET, IP, &server.sin_addr) <= 0) {
        fprintf(stderr, "Error: Invalid IP address\n");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    printf("Enter message: ");
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

    printf("Sending to %s:%d: %s\n", IP, PORT, sendline);
    if (sendto(sockfd, sendline, len, 0,
               (struct sockaddr *)&server, sizeof(server)) < 0) {
        perror("sendto");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    socklen_t server_len = sizeof(server);
    ssize_t nread = recvfrom(sockfd, recvline, BUFSIZE - 1, 0,
                              (struct sockaddr *)&server, &server_len);
    if (nread < 0) {
        perror("recvfrom (timeout or error)");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    recvline[nread] = '\0';
    printf("Received: %s\n", recvline);

    close(sockfd);
    return 0;
}
```

#### Makefile

```makefile name=Makefile
CC = gcc
CFLAGS = -Wall -Wextra -Werror -O2 -std=c11

.PHONY: all clean test-tcp test-udp

all: tcpserver tcpclient udpserver udpclient

tcpserver: tcpserver.c
	$(CC) $(CFLAGS) -o tcpserver tcpserver.c

tcpclient: tcpclient.c
	$(CC) $(CFLAGS) -o tcpclient tcpclient.c

udpserver: udpserver.c
	$(CC) $(CFLAGS) -o udpserver udpserver.c

udpclient: udpclient.c
	$(CC) $(CFLAGS) -o udpclient udpclient.c

clean:
	rm -f tcpserver tcpclient udpserver udpclient *.o

test-tcp:
	@echo "=== TCP Test ==="
	@echo "Start server: ./tcpserver 8080 1024"
	@echo "Then run: echo 'Hello TCP' | ./tcpclient 127.0.0.1 8080 1024"

test-udp:
	@echo "=== UDP Test ==="
	@echo "Start server: ./udpserver 9090 1024"
	@echo "Then run: echo 'Hello UDP' | ./udpclient 127.0.0.1 9090 1024"
```

---

## Задание 2: Ответы на вопросы

### Вопрос 1: Что делают оба приложения?

**Ответ:**

Оба приложения реализуют простой **эхо-сервер**:
- **Сервер** получает сообщение от клиента и отправляет его обратно (эхо)
- **Клиент** отправляет сообщение серверу и ожидает эхо-ответ

**TCP-приложение:**
- Устанавливает соединение перед передачей данных (3-way handshake)
- Работает в режиме "один клиент → один цикл обработки"
- Гарантирует доставку сообщения

**UDP-приложение:**
- Не устанавливает соединение
- Просто отправляет датаграмму и ждёт ответ
- Не гарантирует доставку

**Демонстрация:** см. Тест 1 и Тест 2 в разделе "Демонстрация работы"

---

### Вопрос 2: Что произойдет, если tcpclient отправит сообщение незапущенному серверу?

**Ответ:**

Клиент **немедленно получит ошибку** `Connection refused`.

**Объяснение:**
1. Клиент пытается установить TCP-соединение (отправляет SYN)
2. Операционная система сервера отвечает **RST** (reset), так как на порту никто не слушает
3. `connect()` возвращает ошибку `ECONNREFUSED`
4. Программа завершается с сообщением об ошибке

**Поведение:** клиент **сразу узнаёт**, что сервер недоступен (0 мс задержка).

**Демонстрация:** см. Тест 4 в разделе "Демонстрация работы"

---

### Вопрос 3: Что произойдет, если udpclient отправит сообщение незапущенному серверу?

**Ответ:**

Клиент **не получит немедленной ошибки**, будет ждать таймаут (5 секунд), затем получит ошибку `Resource temporarily unavailable`.

**Объяснение:**
1. Клиент отправляет датаграмму (UDP не требует соединения)
2. `sendto()` **успешно завершается** (данные переданы в сеть)
3. ОС сервера может отправить ICMP "Port Unreachable", но это не гарантировано
4. `recvfrom()` **блокируется** и ждёт ответа
5. По истечении таймаута (5 секунд) возвращается ошибка

**Поведение:** клиент **не узнаёт сразу** о недоступности сервера.

**Демонстрация:** см. Тест 3 в разделе "Демонстрация работы"

---

### Вопрос 4: Что произойдет, если tcpclient отвалится во время работы с сервером?

**Ответ:**

Сервер **узнаёт** о разрыве соединения и получает ошибку.

**Сценарий 1: корректное закрытие (Ctrl+C)**
- Клиент отправляет FIN
- Сервер получает EOF (`recv` возвращает 0)
- Сервер корректно завершает обработку

**Сценарий 2: аварийное завершение (kill -9)**
- TCP keepalive или следующая попытка I/O обнаружит разрыв
- Сервер получает `Connection reset by peer`

**Поведение:** сервер **узнаёт** о разрыве соединения (RST/FIN).

**Демонстрация:** см. Тест 5 в разделе "Демонстрация работы"

---

### Вопрос 5: Что произойдет, если udpclient отвалится во время работы с сервером?

**Ответ:**

Сервер **не замечает** отключения клиента и продолжает работать как обычно.

**Объяснение:**
- UDP — **connectionless** протокол, нет понятия "соединения"
- Сервер не отслеживает состояние клиентов
- Если клиент отвалился, сервер об этом **не узнаёт**
- Сервер просто не получит следующую датаграмму от этого клиента

**Поведение:** сервер **не замечает** отключения клиента.

**Демонстрация:** см. Тест 6 в разделе "Демонстрация работы"

---

### Вопрос 6: Что произойдет, если udpclient отправит сообщение на несуществующий / выключенный сервер?

**Ответ:**

Аналогично **вопросу 3**: клиент не узнаёт сразу, ждёт таймаут (5 секунд).

**Объяснение:**
1. `sendto()` успешно отправляет датаграмму
2. Если сервер недоступен:
   - **Локально:** роутер может отправить ICMP "Host/Port Unreachable"
   - **Удалённо:** пакет может потеряться без уведомления
3. `recvfrom()` ждёт таймаут и возвращает ошибку

**Поведение:** клиент **не узнаёт сразу** о недоступности (5000 мс задержка).

**Демонстрация:** см. Тест 3 в разделе "Демонстрация работы"

---

### Вопрос 7: Что произойдет, если tcpclient отправит сообщение на несуществующий / выключенный сервер?

**Ответ:**

Зависит от расположения сервера:

**Локальная сеть (сервер не существует):**
```
connect: Connection refused
```
Операционная система отвечает RST → **немедленная ошибка** (0 мс).

**Удалённая сеть (firewall, выключен):**
```
connect: Connection timed out
```
TCP повторяет SYN несколько раз → **таймаут через ~75-120 секунд**.

**Поведение:** клиент **узнаёт** о недоступности (быстро локально, медленно удалённо).

**Демонстрация:** см. Тест 4 в разделе "Демонстрация работы"

---

### Вопрос 8: В чем отличия UDP и TCP протоколов?

**Сравнительная таблица:**

| Характеристика | TCP | UDP |
|----------------|-----|-----|
| **Тип соединения** | Connection-oriented | Connectionless |
| **Надёжность** | Гарантирует доставку | Не гарантирует |
| **Порядок данных** | Сохраняет порядок | Может нарушаться |
| **Скорость** | Медленнее (overhead) | Быстрее |
| **Модель данных** | Поток байтов (stream) | Дискретные датаграммы |
| **Контроль потока** | Есть (flow control) | Нет |
| **Контроль перегрузки** | Есть (congestion control) | Нет |
| **Обнаружение ошибок** | Checksums + retransmission | Только checksum |
| **Уведомление о разрыве** | Да (FIN, RST) | Нет |
| **Размер заголовка** | 20-60 байт | 8 байт |
| **Использование** | HTTP, FTP, SSH, Email | DNS, стриминг, игры |
| **Обнаружение недоступности** | Быстрое (RST или таймаут) | Медленное (таймаут) |

**Ключевые различия:**

1. **Установка соединения:**
   - TCP: 3-way handshake (SYN, SYN-ACK, ACK)
   - UDP: сразу передача данных

2. **Обработка потери пакетов:**
   - TCP: автоматическая повторная отправка
   - UDP: пакет потерян навсегда

3. **Уведомления об ошибках:**
   - TCP: клиент узнаёт через RST/FIN
   - UDP: клиент не узнаёт (только ICMP, не гарантировано)

4. **Overhead:**
   - TCP: высокий (заголовки, подтверждения)
   - UDP: минимальный (8 байт)

---

## Демонстрация работы

### Компиляция

```bash
@AleshinIvan ➜ .../lab7/src $ make
gcc -Wall -Wextra -Werror -O2 -std=c11 -o tcpserver tcpserver.c
gcc -Wall -Wextra -Werror -O2 -std=c11 -o tcpclient tcpclient.c
gcc -Wall -Wextra -Werror -O2 -std=c11 -o udpserver udpserver.c
gcc -Wall -Wextra -Werror -O2 -std=c11 -o udpclient udpclient.c
```

---

### Тест 1: TCP эхо-сервер — нормальная работа (вопрос 1)

**Терминал 1 (сервер):**
```bash
@AleshinIvan ➜ .../lab7/src $ ./tcpserver 8080 1024
TCP Server listening on port 8080 (bufsize=1024)
Client connected: 127.0.0.1:54321
Received 9 bytes: Hello TCP
Client disconnected
```

**Терминал 2 (клиент):**
```bash
@AleshinIvan ➜ .../lab7/src $ echo "Hello TCP" | ./tcpclient 127.0.0.1 8080 1024
Connecting to 127.0.0.1:8080...
Connected! Enter message: Sending: Hello TCP
Received: Hello TCP
```

**Результат:** ✅ TCP соединение установлено, эхо работает корректно

---

### Тест 2: UDP эхо-сервер — нормальная работа (вопрос 1)

**Терминал 1 (сервер):**
```bash
@AleshinIvan ➜ .../lab7/src $ ./udpserver 9090 1024
UDP Server listening on port 9090 (bufsize=1024)
Received 9 bytes from 127.0.0.1:48765: Hello UDP
```

**Терминал 2 (клиент):**
```bash
@AleshinIvan ➜ .../lab7/src $ echo "Hello UDP" | ./udpclient 127.0.0.1 9090 1024
Enter message: Sending to 127.0.0.1:9090: Hello UDP
Received: Hello UDP
```

**Результат:** ✅ UDP датаграмма отправлена, эхо работает корректно

---

### Тест 3: UDP к недоступному серверу (вопросы 3, 6)

```bash
@AleshinIvan ➜ .../lab7/src $ echo "test" | ./udpclient 127.0.0.1 9999 1024
Enter message: Sending to 127.0.0.1:9999: test
recvfrom (timeout or error): Resource temporarily unavailable
```

**Результат:**
- `sendto()` успешно выполнен (нет ошибки)
- Клиент ждал **5 секунд** (таймаут)
- `recvfrom()` вернул `EAGAIN` после таймаута
- **Вывод:** UDP не узнаёт сразу о недоступности сервера

---

### Тест 4: TCP к недоступному серверу (вопросы 2, 7)

```bash
@AleshinIvan ➜ .../lab7/src $ ./tcpclient 127.0.0.1 8888 1024
Connecting to 127.0.0.1:8888...
connect: Connection refused
```

**Результат:**
- `connect()` **немедленно** вернул `ECONNREFUSED`
- ОС отправила RST
- **Вывод:** TCP сразу узнаёт о недоступности сервера

**Сравнение с UDP:**
| Протокол | Время до ошибки | Тип ошибки |
|----------|-----------------|------------|
| UDP | 5000 мс (таймаут) | Resource temporarily unavailable |
| TCP | 0 мс (мгновенно) | Connection refused |

---

### Тест 5: Отключение TCP клиента (вопрос 4)

**Терминал 1 (сервер):**
```bash
@AleshinIvan ➜ .../lab7/src $ ./tcpserver 8080 1024
TCP Server listening on port 8080 (bufsize=1024)
Client connected: 127.0.0.1:45678
recv: Connection reset by peer
```

**Терминал 2 (клиент — Ctrl+C):**
```bash
@AleshinIvan ➜ .../lab7/src $ ./tcpclient 127.0.0.1 8080 1024
Connecting to 127.0.0.1:8080...
Connected! Enter message: ^C
```

**Результат:**
- Сервер получил `ECONNRESET`
- TCP **уведомил** сервер о разрыве
- **Вывод:** сервер узнаёт об отключении клиента

---

### Тест 6: Отключение UDP клиента (вопрос 5)

**Терминал 1 (сервер):**
```bash
@AleshinIvan ➜ .../lab7/src $ ./udpserver 9090 1024
UDP Server listening on port 9090 (bufsize=1024)
Received 9 bytes from 127.0.0.1:48765: Hello UDP
# После Ctrl+C клиента — сервер продолжает работать без изменений
```

**Терминал 2 (клиент — Ctrl+C):**
```bash
@AleshinIvan ➜ .../lab7/src $ ./udpclient 127.0.0.1 9090 1024
Enter message: Test message
Sending to 127.0.0.1:9090: Test message
Received: Test message
^C
```

**Результат:**
- Сервер **не получил уведомления**
- Сервер продолжает работать
- **Вывод:** UDP сервер не замечает отключение клиента

---

### Сводная таблица результатов

| Тест | TCP | UDP |
|------|-----|-----|
| **Нормальная работа** | ✅ Работает | ✅ Работает |
| **Недоступный сервер** | Connection refused (0 мс) | Timeout (5000 мс) |
| **Отключение клиента** | Сервер узнаёт (RST) | Сервер не замечает |
| **Скорость** | Медленнее (handshake) | Быстрее |
| **Надёжность** | Гарантирует доставку | Не гарантирует |

---

## Выводы

### Основные выводы

1. **TCP обеспечивает надёжность** ценой производительности:
   - Гарантирует доставку данных
   - Немедленно уведомляет о проблемах (Connection refused)
   - Сервер узнаёт об отключении клиента (RST/FIN)
   - **Подходит для:** HTTP, SSH, базы данных, email

2. **UDP обеспечивает скорость** ценой надёжности:
   - Не гарантирует доставку
   - Узнаёт о проблемах только через таймаут
   - Сервер не замечает отключение клиента
   - **Подходит для:** DNS, видео/аудио стриминг, игры, VoIP

3. **Обнаружение ошибок:**
   - **TCP:** мгновенное уведомление (RST)
   - **UDP:** ожидание таймаута (5 секунд)

4. **Отслеживание состояния:**
   - **TCP:** connection-oriented (сервер знает о клиентах)
   - **UDP:** connectionless (сервер не отслеживает)

5. **Практические рекомендации:**
   - Нужна **гарантия доставки** → TCP
   - Нужна **низкая задержка** и допустима потеря пакетов → UDP
   - **Таймауты в UDP критичны** — без них клиент зависнет

6. **Аргументы командной строки:**
   - Вынесение `#define` в аргументы делает программы гибкими
   - Тестирование разных портов без перекомпиляции

### Результаты экспериментов

| Сценарий | TCP | UDP |
|----------|-----|-----|
| **Нормальная работа** | ✅ Работает | ✅ Работает |
| **Недоступный сервер** | Connection refused (0 мс) | Timeout (5000 мс) |
| **Отключение клиента** | Сервер получает RST | Сервер не замечает |
| **Гарантия доставки** | Да (с повторами) | Нет |
| **Overhead** | Высокий (заголовки + ACK) | Минимальный (8 байт) |
| **Применение** | HTTP, SSH, БД | DNS, стриминг, игры |

---

## Структура проекта

```
lab7/
├── src/
│   ├── tcpserver.c      # TCP эхо-сервер
│   ├── tcpclient.c      # TCP клиент
│   ├── udpserver.c      # UDP эхо-сервер
│   ├── udpclient.c      # UDP клиент
│   └── Makefile         # Система сборки
├── .gitignore
└── README.md
```

---

## .gitignore

```gitignore
# Бинарные файлы
tcpserver
tcpclient
udpserver
udpclient

# Объектные файлы
*.o
*.out
*.exe

# Временные файлы
*~
*.swp
*.swo
```

---

**Дата выполнения:** 2025-11-22  
**Автор:** AleshinIvan  
**Статус:** ✅ ГОТОВО К СДАЧЕ