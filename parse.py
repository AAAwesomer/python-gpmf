# TODO: Implement GPMF parsing
#   see https://github.com/gopro/gpmf-parser#gmfp-deeper-dive for format details
"""Parses the FOURCC data in GPMF stream into fields"""
import construct
import sys
import datetime
from itertools import islice
from math import floor

TYPES = construct.Enum(
    construct.Byte,
    int8_t=ord(b'b'),
    uint8_t=ord(b'B'),
    char=ord(b'c'),
    int16_t=ord(b's'),
    uint16_t=ord(b'S'),
    int32_t=ord(b'l'),
    uint32_t=ord(b'L'),
    float=ord(b'f'),
    double=ord(b'd'),
    fourcc=ord(b'F'),
    uuid=ord(b'G'),
    int64_t=ord(b'j'),
    uint64_t=ord(b'J'),
    Q1516=ord(b'q'),
    Q3132=ord(b'Q'),
    utcdate=ord(b'U'),
    complex=ord(b'?'),
    nested=0x0,
)

FOURCC = construct.Struct(
    "key" / construct.Bytes(4),
    "type" / construct.Byte,
    "size" / construct.Byte,
    "repeat" / construct.Int16ub,
    "data" / construct.Aligned(4, construct.Bytes(construct.this.size * construct.this.repeat))
)


def recursive(data, parents=tuple()):
    """Recursive parser returns depth-first traversing generator yielding fields and list of their parent keys"""
    elements = FOURCC[:].parse(data)
    for element in elements:
        if element.type == 0:
            subparents = parents + (element.key,)
            for subyield in recursive(element.data, subparents):
                yield subyield
        else:
            yield (element, parents)

def get_time(data):

    d = recursive(data)
    for element, parents in d:
        if element["key"] == b"GPSU":
            time = str(element['data'].decode('UTF-8'))
            years = int(time[:2])
            months = int(time[2:4])
            days = int(time[4:6])
            hours = int(time[6:8])
            minutes = int(time[8:10])
            seconds = int(floor(float(time[10:])))
            timestamp = datetime.datetime(2000+years, months, days, hours, minutes, seconds)
            return timestamp

if __name__ == "__main__":
    get_time("./vids/GOPR0047.MP4")