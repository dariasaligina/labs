import sys
import random

try:
    A = int(sys.stdin.readline().strip())
    B = random.randint(-10, 10)
    result = A / B
    print(result)
except Exception as e:
    print(f"Ошибка: {e}", file=sys.stderr)
