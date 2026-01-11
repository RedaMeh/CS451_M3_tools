import sys
import random
from pathlib import Path

def usage():
    print("Usage: python generate_la_configs.py x y a b c R")
    print("  x = number of config files")
    print("  y = max integers per proposal line (k is drawn from 1..y)")
    print("  a = number of proposal lines")
    print("  b, c = second and third integers on first line")
    print("  R = range size per proposal line (disjoint blocks)")
    print()
    print("Example: x=3 processes, a=3 lines, R=15 ->")
    print("  line1 draws from [1..15], line2 from [16..30], line3 from [31..45]")
    sys.exit(1)

if len(sys.argv) != 7:
    usage()

try:
    x = int(sys.argv[1])
    y = int(sys.argv[2])
    a = int(sys.argv[3])
    b = int(sys.argv[4])
    c = int(sys.argv[5])
    R = int(sys.argv[6])
except ValueError:
    print("All arguments must be integers.")
    usage()

if x <= 0 or a <= 0 or y < 0 or R <= 0:
    print("Invalid values: require x>0, a>0, y>=0, R>0")
    sys.exit(1)

base_dir = Path(__file__).parent

for i in range(1, x + 1):
    filename = base_dir / f"lattice-agreement-{i}.config"
    with open(filename, "w") as f:
        # First line
        f.write(f"{a} {b} {c}\n")

        # Proposal lines
        for j in range(a):
            # Disjoint range per line (1-based values)
            start = j * R
            end = ((j + 1) * R) - 1
            line_range = list(range(start, end + 1))

            if y == 0:
                # If you really allow y=0, write an empty line (or skip)
                f.write("\n")
                continue

            # Can't sample more than the available range size
            k = random.randint(1, min(y, len(line_range)))
            values = random.sample(line_range, k)
            f.write(" ".join(map(str, values)) + "\n")

    print(f"Generated {filename}")
