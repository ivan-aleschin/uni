#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/wait.h>
#include <string.h>
#include <errno.h>

pid_t *child_pids = NULL;
int child_count = 0;
int timeout = 0;

void handle_alarm(int sig) {
    printf("Timeout reached! Sending SIGKILL to child processes...\n");
    for (int i = 0; i < child_count; i++) {
        if (child_pids[i] > 0) {
            kill(child_pids[i], SIGKILL);
        }
    }
}

void find_min(int start, int end, int *array) {
    int min = array[start];
    printf("Дочерний процесс поиска минимума (PID: %d) начал работу\n", getpid());
    for (int i = start + 1; i < end; i++) {
        if (array[i] < min) min = array[i];
        sleep(1); // Имитация долгой работы
    }
    printf("Child %d: min = %d\n", getpid(), min);
    exit(0);
}

void find_max(int start, int end, int *array) {
    int max = array[start];
    printf("Дочерний процесс поиска максимума (PID: %d) начал работу\n", getpid());
    for (int i = start + 1; i < end; i++) {
        if (array[i] > max) max = array[i];
        sleep(1); // Имитация долгой работы
    }
    printf("Child %d: max = %d\n", getpid(), max);
    exit(0);
}

int main(int argc, char *argv[]) {
    // Парсинг аргументов командной строки
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--timeout") == 0 && i + 1 < argc) {
            timeout = atoi(argv[i + 1]);
            i++;
        }
    }

    int array[] = {5, 2, 8, 1, 9, 3, 7, 4, 6, 0};
    int size = sizeof(array) / sizeof(array[0]);
    
    child_pids = malloc(2 * sizeof(pid_t));
    child_count = 2;

    printf("Создание дочерних процессов...\n");
    for (int i = 0; i < 2; i++) {
        pid_t pid = fork();
        
        if (pid == 0) {
            // Дочерний процесс
            if (i == 0) {
                find_min(0, size, array);
            } else {
                find_max(0, size, array);
            }
        } else if (pid > 0) {
            child_pids[i] = pid;
            printf("Создан дочерний процесс PID: %d\n", pid);
        } else {
            perror("fork failed");
            exit(1);
        }
    }

    if (timeout > 0) {
        printf("Установлен таймаут: %d секунд\n", timeout);
        signal(SIGALRM, handle_alarm);
        alarm(timeout);
    } else {
        printf("Таймаут не установлен\n");
    }

    int completed = 0;
    printf("Ожидание завершения дочерних процессов...\n");
    
    while (completed < child_count) {
        int status;
        pid_t result = waitpid(-1, &status, WNOHANG);
        
        if (result > 0) {
            if (WIFEXITED(status)) {
                printf("Child %d завершился нормально со статусом: %d\n", result, WEXITSTATUS(status));
            } else if (WIFSIGNALED(status)) {
                printf("Child %d завершен по сигналу: %d\n", result, WTERMSIG(status));
            }
            completed++;
        } else if (result == 0) {
            printf("Дочерние процессы еще работают...\n");
            sleep(1);
        } else {
            if (errno == ECHILD) {
                printf("Все дочерние процессы завершены\n");
                break;
            }
            perror("waitpid failed");
            break;
        }
    }

    free(child_pids);
    printf("Родительский процесс завершен\n");
    return 0;
}