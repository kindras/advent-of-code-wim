"""
--- Day 16: Packet Decoder ---
https://adventofcode.com/2021/day/16
"""
import io
import math
from aocd import data


def literal():
    pass


def gt(vals):
    a, b = vals
    return 1 if a > b else 0


def lt(vals):
    a, b = vals
    return 1 if a < b else 0


def eq(vals):
    a, b = vals
    return 1 if a == b else 0


ops = {
    "+": sum,
    "*": math.prod,
    "min": min,
    "max": max,
    "val": literal,
    ">": gt,
    "<": lt,
    "==": eq,
}
op_types = [*ops.items()]
decoded_stream = []


class Packet:
    def __init__(self, stream):
        self.n_read = 0
        self.stream = stream
        self.version = self.read_int(3)
        type_id = self.read_int(3)
        glyph, self.func = op_types[type_id]
        self.subpackets = []
        if self.func is literal:
            nibbles = []
            prefix = 1
            while prefix:
                prefix = self.read_int(1)
                nibbles.append(self.read_raw(4))
            self.value = int("".join(nibbles), 2)
            decoded_stream.append(str(self.value))
        else:  # operator packet
            decoded_stream.append(glyph)
            self.length_type_id = self.read_int(1)
            if self.length_type_id == 0:
                total_length = self.read_int(15)
                subpackets_raw = self.read_raw(total_length)
                substream = io.StringIO(subpackets_raw)
                while total_length:
                    try:
                        subpacket = Packet(substream)
                    except EOFError:
                        break
                    total_length -= subpacket.n_read
                    self.subpackets.append(subpacket)
            else:
                number_of_subpackets = self.read_int(11)
                while number_of_subpackets:
                    try:
                        subpacket = Packet(self.stream)
                    except EOFError:
                        break
                    number_of_subpackets -= 1
                    self.subpackets.append(subpacket)
            vals = [p.value for p in self.subpackets]
            self.value = self.func(vals)

    def read_raw(self, nbits):
        raw = self.stream.read(nbits)
        if len(raw) < nbits:
            raise EOFError
        self.n_read += nbits
        return raw

    def read_int(self, nbits):
        return int(self.read_raw(nbits), 2)

    def __str__(self):
        return f"<Packet v={self.version}, op={self.func.__name__}, val={self.value}>"


stream = io.StringIO("".join([f"{int(x, 16):04b}" for x in data]))
packet0 = Packet(stream)

versions = []
stack = [packet0]
while stack:  # dfs
    packet = stack.pop()
    print(packet)
    versions.append(packet.version)
    stack.extend(packet.subpackets)
print(" ".join(decoded_stream))

print("part a:", sum(versions))
print("part b:", packet0.value)