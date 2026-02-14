#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>

pthread_mutex_t mutex1 = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t mutex2 = PTHREAD_MUTEX_INITIALIZER;

// Решение: оба потока захватывают мьютексы в одинаковом порядке
void* thread_function(void* arg) {
    int thread_id = *(int*)arg;
    
    printf("Thread %d: Trying to lock mutex1...\n", thread_id);
    pthread_mutex_lock(&mutex1);
    printf("Thread %d: Locked mutex1\n", thread_id);
    
    sleep(1);
    
    printf("Thread %d: Trying to lock mutex2...\n", thread_id);
    pthread_mutex_lock(&mutex2);
    printf("Thread %d: Locked mutex2\n", thread_id);
    
    printf("Thread %d: Inside critical section\n", thread_id);
    
    pthread_mutex_unlock(&mutex2);
    pthread_mutex_unlock(&mutex1);
    
    printf("Thread %d: Released all locks\n", thread_id);
    
    return NULL;
}

int main() {
    pthread_t thread1, thread2;
    int id1 = 1, id2 = 2;
    
    printf("=== Deadlock Fixed ===\n");
    printf("Both threads lock mutexes in the same order\n");
    printf("======================\n\n");
    
    pthread_create(&thread1, NULL, thread_function, &id1);
    pthread_create(&thread2, NULL, thread_function, &id2);
    
    pthread_join(thread1, NULL);
    pthread_join(thread2, NULL);
    
    printf("\nAll threads completed successfully!\n");
    
    return 0;
}