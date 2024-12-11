import sys
import random

try:
    A = int(sys.stdin.readline().strip())
    B = random.randint(-10, 10)
    result = A / B
    print(result)
    with open('logs.txt', 'a') as f:
        f.write(f"A = {A}, B = {B}, A/B={result}\n")
except Exception as e:
    with open('errors.txt', 'a') as f:
        print(f"Error: {e}", file=f)