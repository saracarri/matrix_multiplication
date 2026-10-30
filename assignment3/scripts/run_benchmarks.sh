#!/bin/bash

set -e

mkdir -p results

rm -f results/sequential_times.csv
rm -f results/sequential_memory.csv
rm -f results/parallel_*_threads_times.csv
rm -f results/parallel_*_threads_memory.csv

echo "Compiling implementations..."

gcc -O2 -std=c11 c/sequential.c -o c/sequential.exe
gcc -O2 -std=c11 -fopenmp c/parallel.c -o c/parallel.exe

echo "Running correctness tests..."

./c/sequential.exe --test
OMP_NUM_THREADS=4 ./c/parallel.exe --test

echo "Running sequential benchmarks..."

for n in 100 300 500 750 1000; do
    ./c/sequential.exe "$n"
done

echo "Running parallel benchmarks..."

for threads in 1 2 4 8 16 22; do
    for n in 100 300 500 750 1000; do
        echo "Threads: $threads | Size: $n"
        OMP_NUM_THREADS=$threads ./c/parallel.exe "$n"
    done
done

echo "Benchmarks completed."