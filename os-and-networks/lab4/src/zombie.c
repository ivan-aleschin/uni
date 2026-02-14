#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main() {
    printf("Демонстрация зомби-процессов\n");
    printf("Создание дочернего процесса...\n");
    
    pid_t pid = fork();
    
    if (pid == 0) {
        // Дочерний процесс
        printf("Дочерний процесс (PID: %d) запущен\n", getpid());
        printf("Дочерний процесс завершается через 2 секунды...\n");
        sleep(2);
        printf("Дочерний процесс завершен\n");
        exit(0);
    } else if (pid > 0) {
        // Родительский процесс
        printf("Родительский процесс (PID: %d) создал дочерний %d\n", getpid(), pid);
        printf("Родительский процесс засыпает на 10 секунд...\n");
        printf("В это время выполните в другом терминале:\n");
        printf("ps aux | grep %d\n", pid);
        printf("чтобы увидеть зомби-процесс (статус Z)\n\n");
        
        sleep(10); // Даем время увидеть зомби
        
        printf("\nРодительский процесс просыпается и вызывает wait()...\n");
        int status;
        wait(&status);
        printf("Зомби-процесс убран (wait вернул статус: %d)\n", status);
    } else {
        perror("fork failed");
        return 1;
    }
    
    printf("Программа завершена\n");
    return 0;
}