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

# Тестовые запуски (демонстрация)
test-tcp:
	@echo "=== TCP Test ==="
	@echo "Start server in another terminal: ./tcpserver 8080 1024"
	@echo "Then run: echo 'Hello TCP' | ./tcpclient 127.0.0.1 8080 1024"

test-udp:
	@echo "=== UDP Test ==="
	@echo "Start server in another terminal: ./udpserver 9090 1024"
	@echo "Then run: echo 'Hello UDP' | ./udpclient 127.0.0.1 9090 1024"