#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <getopt.h>

typedef struct {
    int start;
    int end;
    int mod;
    long long partial_result;
} ThreadData;

pthread_mutex_t result_mutex = PTHREAD_MUTEX_INITIALIZER;
long long global_result = 1;

void* calculate_partial_factorial(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    long long local_result = 1;
    
    for (int i = data->start; i <= data->end; i++) {
        local_result = (local_result * i) % data->mod;
    }
    
    data->partial_result = local_result;
    
    // Синхронизированное обновление глобального результата
    pthread_mutex_lock(&result_mutex);
    global_result = (global_result * local_result) % data->mod;
    pthread_mutex_unlock(&result_mutex);
    
    return NULL;
}

int main(int argc, char* argv[]) {
    int k = 0;
    int pnum = 1;
    int mod = 1000000007;
    
    // Парсинг аргументов командной строки
    static struct option long_options[] = {
        {"pnum", required_argument, 0, 'p'},
        {"mod",  required_argument, 0, 'm'},
        {0, 0, 0, 0}
    };
    
    int opt;
    int option_index = 0;
    
    while ((opt = getopt_long(argc, argv, "k:p:m:", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'k':
                k = atoi(optarg);
                break;
            case 'p':
                pnum = atoi(optarg);
                break;
            case 'm':
                mod = atoi(optarg);
                break;
            default:
                fprintf(stderr, "Usage: %s -k <number> --pnum=<threads> --mod=<modulo>\n", argv[0]);
                fprintf(stderr, "Example: %s -k 10 --pnum=4 --mod=10\n", argv[0]);
                exit(EXIT_FAILURE);
        }
    }
    
    if (k <= 0 || pnum <= 0 || mod <= 0) {
        fprintf(stderr, "Error: k, pnum, and mod must be positive integers\n");
        exit(EXIT_FAILURE);
    }
    
    printf("Computing %d! mod %d using %d threads\n", k, mod, pnum);
    
    pthread_t threads[pnum];
    ThreadData thread_data[pnum];
    
    int range = k / pnum;
    int remainder = k % pnum;
    int start = 1;
    
    // Создание потоков
    for (int i = 0; i < pnum; i++) {
        thread_data[i].start = start;
        thread_data[i].end = start + range - 1;
        
        // Добавляем остаток к последнему потоку
        if (i == pnum - 1) {
            thread_data[i].end += remainder;
        }
        
        thread_data[i].mod = mod;
        thread_data[i].partial_result = 1;
        
        printf("Thread %d: calculating from %d to %d\n", 
               i, thread_data[i].start, thread_data[i].end);
        
        if (pthread_create(&threads[i], NULL, calculate_partial_factorial, 
                          &thread_data[i]) != 0) {
            perror("pthread_create");
            exit(EXIT_FAILURE);
        }
        
        start = thread_data[i].end + 1;
    }
    
    // Ожидание завершения всех потоков
    for (int i = 0; i < pnum; i++) {
        if (pthread_join(threads[i], NULL) != 0) {
            perror("pthread_join");
            exit(EXIT_FAILURE);
        }
        printf("Thread %d finished with partial result: %lld\n", 
               i, thread_data[i].partial_result);
    }
    
    printf("\nResult: %d! mod %d = %lld\n", k, mod, global_result);
    
    pthread_mutex_destroy(&result_mutex);
    
    return 0;
}