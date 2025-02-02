#!/usr/bin/python3
import os
import sys
import subprocess
import threading

results = []

input = ""
output = ""

args = sys.argv

args.pop(0)

v = False
o = False

for arg in args:
    if arg == "-v":
        v = True
    elif arg == "-o":
        o = True
    elif o:
        output = arg
        o = False
    else:
        input = arg

def xznicer_loop(range1, range2, thread):
    command = f"xz --format=xz -9 --extreme --keep --stdout {input} > /tmp/out{thread}.xz --lzma2=preset=9,lc=0,lp=0,pb=0,nice="
    progress = 0
    total_steps = range2 - range1
    if total_steps != 0:
        tick = 100.0 / total_steps
    else:
        tick = 0

    for i in range(range1, range2):
        exe = command + str(i)
        exe += f" && wc -c /tmp/out{thread}.xz && rm /tmp/out{thread}.xz"
        result = os.popen(exe).read().strip()
        if result:
            size = int(result.split(" ")[0])
            results.append([size, str(i)])
        else:
            print(f"Warning: No output for nice={i}, skipping.")
        progress += tick
        print(f"Thread {thread}: Finding optimal LZMA2-nice-parameter {int(progress)}%", end="\r")

def xznicer_thread(thread_id, range_start, range_end):
    xznicer_loop(range_start, range_end, thread_id)

def xznicer():
    # Define the ranges for each thread
    total_range = 274 - 4
    step = total_range // 4
    ranges = [
        (4, 4 + step),
        (4 + step, 4 + 2 * step),
        (4 + 2 * step, 4 + 3 * step),
        (4 + 3 * step, 274)
    ]

    threads = []
    for i in range(4):
        t = threading.Thread(target=xznicer_thread, args=(i+1, ranges[i][0], ranges[i][1]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    results.sort(key=lambda x: x[0])

    if v:
        for row in results:
            print(row)
    print("Best choice:")
    print("nice=" + str(results[0][1]), "Uses " + str(results[0][0]) + " bytes")
    exe = f"xz --format=xz -9 --extreme --lzma2=preset=9,lc=0,lp=0,pb=0,nice={results[0][1]} --keep --stdout {input} > {output}"
    print(exe)
    print(os.popen(exe).read())

def main():
    if input == "":
        print("No input file given")
        return
    elif output == "":
        print("No output file given")
        return

    xznicer_loop_thread = threading.Thread(target=xznicer)

    xznicer_loop_thread.start()

    xznicer_loop_thread.join()

if __name__ == "__main__":
    main()
