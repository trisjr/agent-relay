"""Convert a duration to minutes.

Accepted forms: "1h30m", "2h", "45m".

    python3 durations.py 1h30m   ->  90
"""
import sys


def split_parts(text):
    hours, _, rest = text.partition("h")
    return hours, rest.rstrip("m")


def to_minutes(text):
    hours, minutes = split_parts(text.strip().lower())
    return int(hours) * 60 + int(minutes)


if __name__ == "__main__":
    print(to_minutes(sys.argv[1]))
