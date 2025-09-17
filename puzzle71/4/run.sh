# Benchmark with 1 million inputs
python3 ripemd160_cuda.py --benchmark 1000000

# Process specific inputs
python3 ripemd160_cuda.py --input "hello" "world" "bitcoin"

# Process inputs from file
python3 ripemd160_cuda.py --file inputs.txt
