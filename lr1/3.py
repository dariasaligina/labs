import sys
import math

try:
    number = float(sys.stdin.read().strip())
    result = math.sqrt(number)
    with open('output.txt', 'w') as f:
        print(result, file=f)
except Exception as e:
    print(f"Ошибка: {e}", file=sys.stderr)

