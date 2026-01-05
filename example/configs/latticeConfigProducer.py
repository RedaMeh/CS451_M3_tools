import sys
import random
from pathlib import Path

def usage():
    print("Usage: python generate_la_configs.py x y a b c")
    print("  x = number of config files")
    print("  y = max integers per proposal line")
    print("  a = number of proposal lines")
    print("  b, c = second and third integers on first line")
    sys.exit(1)

if len(sys.argv) != 6:
    usage()

try:
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    a = int(sys.argv[3])
    b = int(sys.argv[4])
    c = int(sys.argv[5])
except ValueError:
    print("All arguments must be integers.")
    usage()

if x <= 0 or y < 0 or a <= 0:
    print("Invalid values: require x>0, a>0, y>=0")
    sys.exit(1)

base_dir = Path(__file__).parent
value_range = list(range(1, min(100, 2 * x + 1)))

for i in range(1, x + 1):
    filename = base_dir / f"lattice-agreement-{i}.config"
    with open(filename, "w") as f:
        # First line
        f.write(f"{a} {b} {c}\n")

        # Proposal lines
        for _ in range(a):
            k = random.randint(1, min(y, len(value_range)))
            values = random.sample(value_range, k)
            f.write(" ".join(map(str, values)) + "\n")

    print(f"Generated {filename}")
