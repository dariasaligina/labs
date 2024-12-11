import random
import sys

try:
    A = random.randint(-10, 10)
    print(A)
    with open('logs.txt', 'a') as f:
        f.write(f"A = {A}\n")
except Exception as e:
    with open('errors.txt', 'a') as f:
        print(f"Error: {e}", file=f)
# python 1.py | python 2.py | python 3.py