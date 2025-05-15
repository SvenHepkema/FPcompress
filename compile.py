#!/usr/bin/env python3

import subprocess
import os
import shutil
import time

COMPUTE_CAPABILITY = "61"

def compile_code(command, output_dir):
    try:
        subprocess.run(command, shell=True, check=True)
        print("SUCCESS", command)
    except subprocess.CalledProcessError:
        print("FAILED", command)

def create_bin_folder(src_dir):
    bin_dir = os.path.join(src_dir, 'bin')
    if os.path.exists(bin_dir):
        shutil.rmtree(bin_dir)  # Delete the existing "bin" directory and its contents
    os.makedirs(bin_dir)  # Create a new "bin" directory

def move_executables(src_dir):
    bin_dir = os.path.join(src_dir, 'bin')
    for file in os.listdir(src_dir):
        if "." not in file:
            shutil.move(os.path.join(src_dir, file), bin_dir)

def main():
    src_dir = "single_src"
    create_bin_folder(src_dir)

    # Compile CPU compressors and decompressors
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-cpu-compress')} {os.path.join(src_dir, 'ratio-compressor-single.cpp')}", src_dir)
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-cpu-decompress')} {os.path.join(src_dir, 'ratio-decompressor-single.cpp')}", src_dir)
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'speed-cpu-compress')} {os.path.join(src_dir, 'speed-compressor-single.cpp')}", src_dir)
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'speed-cpu-decompress')} {os.path.join(src_dir, 'speed-decompressor-single.cpp')}", src_dir)

    # Compile GPU compressors and decompressors
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-gpu-compress')} {os.path.join(src_dir, 'ratio-compressor-single.cu')}", src_dir)
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-gpu-decompress')} {os.path.join(src_dir, 'ratio-decompressor-single.cu')}", src_dir)
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'speed-gpu-compress')} {os.path.join(src_dir, 'speed-compressor-single.cu')}", src_dir)
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'speed-gpu-decompress')} {os.path.join(src_dir, 'speed-decompressor-single.cu')}", src_dir)

    move_executables(src_dir)

    src_dir = "double_src"
    create_bin_folder(src_dir)

    # Compile CPU compressors and decompressors
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-cpu-compress')} {os.path.join(src_dir, 'ratio-compressor-double.cpp')}", src_dir)
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-cpu-decompress')} {os.path.join(src_dir, 'ratio-decompressor-double.cpp')}", src_dir)
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'speed-cpu-compress')} {os.path.join(src_dir, 'speed-compressor-double.cpp')}", src_dir)
    #compile_code(f"g++ -O3 -march=native -fopenmp -I. -std=c++17 -o {os.path.join(src_dir, 'speed-cpu-decompress')} {os.path.join(src_dir, 'speed-decompressor-double.cpp')}", src_dir)

    # Compile GPU compressors and decompressors
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-gpu-compress')} {os.path.join(src_dir, 'ratio-compressor-double.cu')}", src_dir)
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'ratio-gpu-decompress')} {os.path.join(src_dir, 'ratio-decompressor-double.cu')}", src_dir)
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'speed-gpu-compress')} {os.path.join(src_dir, 'speed-compressor-double.cu')}", src_dir)
    compile_code(f"nvcc -O3 -arch=sm_{COMPUTE_CAPABILITY} -fmad=false -Xcompiler \"-O3 -march=native -fopenmp\" -I. -std=c++17 -o {os.path.join(src_dir, 'speed-gpu-decompress')} {os.path.join(src_dir, 'speed-decompressor-double.cu')}", src_dir)

    move_executables(src_dir)

if __name__ == "__main__":
    
    # Timing the script
    start_time = time.time()
    
    main()
    
    # Calculate execution time
    execution_time = time.time() - start_time
    print("compile time:\n {:.2f} seconds".format(execution_time))
    print("compiled executables can be found in single_src/bin/ and double_src/bin/")

