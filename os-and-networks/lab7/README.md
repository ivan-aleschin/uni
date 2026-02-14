# Лабораторная работа №7: TCP vs UDP

**Автор:** AleshinIvan  
**Дата:** 2025-11-21

## Описание

Сравнение протоколов TCP и UDP через реализацию эхо-серверов. Оба приложения принимают конфигурацию через аргументы командной строки.

## Структура

```
lab7/
├── src/
│   ├── tcpserver.c      # TCP эхо-сервер
│   ├── tcpclient.c      # TCP клиент
│   ├── udpserver.c      # UDP эхо-сервер
│   ├── udpclient.c      # UDP клиент
│   └── Makefile
├── .gitignore
└── README.md
```

## Компиляция

```bash
cd lab7/src
make
```

Будут созданы: `tcpserver`, `tcpclient`, `udpserver`, `udpclient`

## Использование

### TCP

**Сервер:**
```bash
./tcpserver <port> <bufsize>
# Пример:
./tcpserver 8080 1024
```

**Клиент:**
```bash
./tcpclient <ip> <port> <bufsize>
# Пример:
echo "Hello TCP" | ./tcpclient 127.0.0.1 8080 1024
```

### UDP

**Сервер:**
```bash
./udpserver <port> <bufsize>
# Пример:
./udpserver 9090 1024
```

**Клиент:**
```bash
./udpclient <ip> <port> <bufsize>
# Пример:
echo "Hello UDP" | ./udpclient 127.0.0.1 9090 1024
```

## Примеры тестов

### Тест 1: Нормальная работа TCP

```bash
# Терминал 1:
./tcpserver 8080 1024

# Терминал 2:
echo "Test message" | ./tcpclient 127.0.0.1 8080 1024
```

**Результат:** клиент получит эхо "Test message"

### Тест 2: Нормальная работа UDP

```bash
# Терминал 1:
./udpserver 9090 1024

# Терминал 2:
echo "UDP test" | ./udpclient 127.0.0.1 9090 1024
```

**Результат:** клиент получит эхо "UDP test"

### Тест 3: TCP к незапущенному серверу

```bash
./tcpclient 127.0.0.1 9999 1024
```

**Результат:** 
```
connect: Connection refused
```
(немедленная ошибка)

### Тест 4: UDP к незапущенному серверу

```bash
echo "test" | ./udpclient 127.0.0.1 9999 1024
```

**Результат:**
```
recvfrom (timeout or error): Resource temporarily unavailable
```
(ждёт 5 секунд, затем таймаут)

## Ключевые различия TCP vs UDP

| Особенность | TCP | UDP |
|-------------|-----|-----|
| Соединение | Требуется | Не требуется |
| Надёжность | Гарантирует доставку | Не гарантирует |
| Порядок | Сохраняет | Может нарушаться |
| Скорость | Медленнее | Быстрее |
| Ошибки | Немедленное уведомление | Таймаут |
| Отключение клиента | Сервер узнаёт | Сервер не замечает |

## Очистка

```bash
make clean
```

## Автор

**AleshinIvan**  
Операционные системы и сети, 2025