#!/usr/bin/python3
import os
import sys
import subprocess
import threading

results = []
print_lock = threading.Lock()

input_file = ""
output_file = ""

args = sys.argv
args.pop(0)

verbose = False
output_specified = False

for arg in args:
    if arg == "-v":
        verbose = True
    elif arg == "-o":
        output_specified = True
    elif output_specified:
        output_file = arg
        output_specified = False
    else:
        input_file = arg

def xznicer_test_nices(nice_values, thread_id):
    command_template = f"xz --format=xz -9 --extreme --lzma2=preset=9,lc=0,lp=0,pb=0,nice={{}} --keep --stdout {input_file} > /tmp/out{thread_id}.xz"
    total_steps = len(nice_values)
    if total_steps == 0:
        return
    tick = 100.0 / total_steps
    progress = 0.0

    for idx, nice in enumerate(nice_values):
        command = command_template.format(nice)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode == 0:
            try:
                size = os.path.getsize(f"/tmp/out{thread_id}.xz")
                results.append((size, str(nice)))
            except OSError as e:
                print(f"Error accessing file: {e}")
            finally:
                os.remove(f"/tmp/out{thread_id}.xz")
        else:
            print(f"Warning: 'xz' command failed for nice={nice}, skipping.")
        progress += tick
        with print_lock:
            print(f"Thread {thread_id}: Finding optimal LZMA2-nice-parameter {int(progress)}%", end="\r")

def xznicer():
    num_cores = os.cpu_count() or 1
    nice_values = list(range(2, 274))
    chunk_size = (len(nice_values) + num_cores - 1) // num_cores
    threads = []

    for i in range(num_cores):
        start = i * chunk_size
        end = min(start + chunk_size, len(nice_values))
        chunk = nice_values[start:end]
        if not chunk:
            continue
        thread = threading.Thread(target=xznicer_test_nices, args=(chunk, i+1))
        threads.append(thread)
        thread.start()

    for t in threads:
        t.join()

    results.sort(key=lambda x: x[0])

    if verbose:
        for row in results:
            print(row)
    print("Best choice:")
    best = results[0]
    print(f"nice={best[1]}, Uses {best[0]} bytes")
    final_command = f"xz --format=xz -9 --extreme --lzma2=preset=9,lc=0,lp=0,pb=0,nice={best[1]} --keep --stdout {input_file} > {output_file}"
    print(final_command)
    subprocess.run(final_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    if not input_file:
        print("No input file given")
        return
    elif not output_file:
        print("No output file given")
        return

    xznicer()

if __name__ == "__main__":
    main()
