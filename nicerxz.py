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
    tick = 100.0 / (range2 - range1)

    for i in range(range1, range2):
        exe = command + str(i)
        exe += f" && wc -c /tmp/out{thread}.xz && rm /tmp/out{thread}.xz"
        result = os.popen(exe).read().strip()
        if result:
            size = int(result.split(" ")[0])
            results.append([size, str(i)])
        else:
            print(f"Warning: No output for nice={i}, skipping.", flush=True)
        progress += tick
        print(f"Finding optimal LZMA2-nice-parameter {int(progress)}%", end="\r")

def xznicer1():
    xznicer_loop(4, 274, 1)
    print("\n")

    results.sort(key=lambda x: x[0])

    if v:
        for row in results:
            print(row)
    print("Best choice:")
    print(f"nice={results[0][1]}, Uses {results[0][0]} bytes")
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

    t1 = threading.Thread(target=xznicer1)
    t1.start()
    t1.join()

if __name__ == "__main__":
    main()
