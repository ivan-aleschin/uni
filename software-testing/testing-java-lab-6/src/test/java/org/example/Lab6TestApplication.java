package org.example;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class Lab6TestApplication {

    private static final Logger log = LoggerFactory.getLogger(Lab6TestApplication.class);

    public static void main(String[] args) throws InterruptedException, ExecutionException {
        // Configuration for Ryzen R5 4500 (6 cores/6 threads)
        int n = 10_000_000; // Оптимально для профилирования - factorize() занимает ~80%
        int numThreads = Runtime.getRuntime().availableProcessors();

        log.info("=== Lab 6: Prime Factorization (Multithreaded) ===");
        log.info("Target range: 1 to {}", n);
        log.info("Available processors: {}", numThreads);
        log.info("Creating thread pool with {} threads", numThreads);

        ExecutorService executor = Executors.newFixedThreadPool(numThreads);
        List<Future<FactorizationResult>> futures = new ArrayList<>();

        long startTime = System.currentTimeMillis();
        long startMemory = getUsedMemory();

        // Submit tasks for each number
        for (int i = 1; i <= n; i++) {
            int number = i;
            Callable<FactorizationResult> task = () -> factorize(number);
            futures.add(executor.submit(task));
        }

        // Wait for all tasks to complete and collect results
        int totalFactors = 0;
        for (Future<FactorizationResult> future : futures) {
            FactorizationResult result = future.get();
            totalFactors += result.factors.size();
        }

        long endTime = System.currentTimeMillis();
        long endMemory = getUsedMemory();

        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.MINUTES);

        // Performance metrics
        long executionTime = endTime - startTime;
        long memoryUsed = endMemory - startMemory;

        log.info("=== Results ===");
        log.info("Factorization completed successfully");
        log.info("Execution time: {} ms", executionTime);
        log.info("Total factors found: {}", totalFactors);
        log.info("Memory used: {} MB", memoryUsed / (1024 * 1024));
        log.info("Average time per number: {} μs", (executionTime * 1000.0) / n);
        log.info("Throughput: {} numbers/second", (n * 1000.0) / executionTime);
    }

    /**
     * Factorize a number into its prime factors
     * Optimized algorithm with early termination
     */
    private static FactorizationResult factorize(int number) {
        List<Integer> factors = new ArrayList<>();
        int n = number;

        if (n == 1) {
            factors.add(1);
            return new FactorizationResult(number, factors);
        }

        // Check for factor 2
        while (n % 2 == 0) {
            factors.add(2);
            n /= 2;
        }

        // Check odd factors up to sqrt(n)
        for (int factor = 3; factor * factor <= n; factor += 2) {
            while (n % factor == 0) {
                factors.add(factor);
                n /= factor;
            }
        }

        // If n is still greater than 1, it's a prime factor
        if (n > 1) {
            factors.add(n);
        }

        return new FactorizationResult(number, factors);
    }

    /**
     * Get current memory usage
     */
    private static long getUsedMemory() {
        Runtime runtime = Runtime.getRuntime();
        return runtime.totalMemory() - runtime.freeMemory();
    }

    /**
     * Result container for factorization
     */
    private static class FactorizationResult {
        final int number;
        final List<Integer> factors;

        FactorizationResult(int number, List<Integer> factors) {
            this.number = number;
            this.factors = factors;
        }
    }
}
