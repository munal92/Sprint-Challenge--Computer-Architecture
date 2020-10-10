import sys
from cpu import *


def main(argv):
    """Main."""

    if len(argv) != 2:
        print(f"usage: {argv[0]} filename", file=sys.stderr)
        return 1

    cpu = CPU()

    cpu.load(argv[1])
    cpu.run()

    return 0


main(sys.argv)
