#!/usr/bin/python3
import z3
import struct
import sys

if len(sys.argv) < 2:
    print("Usage: python3 solve.py <float1> <float2> ...")
    sys.exit(1)

try:
    sequence = [float(x) for x in sys.argv[1:]]
except ValueError:
    print("Error: args must be valid floating point numbers.")
    sys.exit(1)

sequence = sequence[::-1]

solver = z3.Solver()

init_A, init_B = z3.BitVecs("A B", 64)

A = init_A
B = init_B

for i in range(len(sequence)):

    a = A
    b = B

    new_A = b

    a ^= a << 23
    a ^= z3.LShR(a, 17)
    a ^= b
    a ^= z3.LShR(b, 26)

    new_B = a

    A = new_A
    B = new_B

    # float to IEEE-754
    float_64 = struct.pack("d", sequence[i] + 1)
    u_long_long_64 = struct.unpack("<Q", float_64)[0]

    mantissa = u_long_long_64 & ((1 << 52) - 1)

    solver.add(z3.LShR(A, 12) == mantissa)

if solver.check() == z3.sat:
    model = solver.model()

    state0 = model.eval(init_A).as_long()
    state1 = model.eval(init_B).as_long()

    print("state0 =", state0)
    print("state1 =", state1)

    u_long_long_64 = (state0 >> 12) | 0x3FF0000000000000
    float_64 = struct.pack("<Q", u_long_long_64)
    next_sequence = struct.unpack("d", float_64)[0] - 1

    print("Next predicted Math.random():", next_sequence)

else:
    print("Solver could not find a solution.")
