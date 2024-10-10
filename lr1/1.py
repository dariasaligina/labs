import random
import sys

try:
    A = random.randint(-10, 10)
    print(A)
except Exception as e:
    print(f"Ошибка: {e}", file=sys.stderr)
