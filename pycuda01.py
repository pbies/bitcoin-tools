#!/usr/bin/env python3

import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import numpy as np

# Define CUDA kernel (executed on the GPU)
cuda_kernel = """
__global__ void vector_add(float *a, float *b, float *c, int n) {
    int idx = threadIdx.x + blockDim.x * blockIdx.x;
    if (idx < n) {
        c[idx] = a[idx] + b[idx];
    }
}
"""

# Compile the kernel
mod = SourceModule(cuda_kernel)

# Get the kernel function
vector_add = mod.get_function("vector_add")

# Vector size
n = 1024

# Create input arrays
a = np.random.randn(n).astype(np.float32)
b = np.random.randn(n).astype(np.float32)

# Allocate memory for the result
c = np.zeros_like(a)

# Allocate GPU memory and copy data to device
a_gpu = cuda.mem_alloc(a.nbytes)
b_gpu = cuda.mem_alloc(b.nbytes)
c_gpu = cuda.mem_alloc(c.nbytes)

cuda.memcpy_htod(a_gpu, a)
cuda.memcpy_htod(b_gpu, b)

# Define grid and block dimensions
threads_per_block = 256
blocks_per_grid = (n + threads_per_block - 1) // threads_per_block

# Launch the kernel
vector_add(a_gpu, b_gpu, c_gpu, np.int32(n), block=(threads_per_block, 1, 1), grid=(blocks_per_grid, 1))

# Copy the result back to host
cuda.memcpy_dtoh(c, c_gpu)

# Verify the result
print("Are the results correct?", np.allclose(c, a + b))
