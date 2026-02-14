CC = gcc
CFLAGS = -Wall -Wextra -Werror -O2 -std=c11
LDFLAGS = -pthread

LIB = libprotocol.a

.PHONY: all clean test kill-servers

all: $(LIB) server client

# Создание библиотеки
$(LIB): protocol.o
	ar rcs $(LIB) protocol.o

protocol.o: protocol.c protocol.h
	$(CC) $(CFLAGS) -c protocol.c

# Компиляция сервера
server: server.o $(LIB)
	$(CC) $(CFLAGS) -o server server.o -L. -lprotocol

server.o: server.c protocol.h
	$(CC) $(CFLAGS) -c server.c

# Компиляция клиента
client: client.o $(LIB)
	$(CC) $(CFLAGS) $(LDFLAGS) -o client client.o -L. -lprotocol

client.o: client.c protocol.h
	$(CC) $(CFLAGS) $(LDFLAGS) -c client.c

# Очистка
clean:
	rm -f server client $(LIB) *.o .server*.pid *.log

# Убить зависшие серверы
kill-servers:
	@echo "Killing any running servers on ports 5001-5004..."
	-@pkill -f './server 500' 2>/dev/null || true
	-@lsof -ti:5001 | xargs kill -9 2>/dev/null || true
	-@lsof -ti:5002 | xargs kill -9 2>/dev/null || true
	-@lsof -ti:5003 | xargs kill -9 2>/dev/null || true
	-@lsof -ti:5004 | xargs kill -9 2>/dev/null || true
	@sleep 1

# Автоматический тест
test: all kill-servers
	@echo "=== Starting test ==="
	@echo "Starting 4 servers..."
	@./server 5001 > server1.log 2>&1 & echo $$! > .server1.pid
	@./server 5002 > server2.log 2>&1 & echo $$! > .server2.pid
	@./server 5003 > server3.log 2>&1 & echo $$! > .server3.pid
	@./server 5004 > server4.log 2>&1 & echo $$! > .server4.pid
	@sleep 2
	@echo "Running client..."
	@./client -k 10 -m 1000 --servers servers.txt
	@echo ""
	@echo "Stopping servers..."
	-@kill `cat .server*.pid` 2>/dev/null || true
	@rm -f .server*.pid
	@echo "=== Test complete ==="