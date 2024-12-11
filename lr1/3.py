import sys
import math

try:
    number = float(sys.stdin.readline().strip())
    result = math.sqrt(number)
    with open('output.txt', 'a') as f:
        print(result, file=f)
    with open('logs.txt', 'a') as f:
        f.write(f"C =  {result}\n")
except Exception as e:
    with open('errors.txt', 'a') as f:
        print(f"Error: {e}", file=f)
