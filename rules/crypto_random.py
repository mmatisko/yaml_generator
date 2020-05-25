import math
import os


class CryptoRandom:
    def __init__(self):
        pass

    @staticmethod
    def random_int(min_: int, max_: int) -> int:
        remain_diff = diff = max_ - min_
        normalized_int: int = 0
        if diff > 0:
            bytes_count = 0
            while remain_diff > 0:
                remain_diff = math.floor(remain_diff / 256)
                bytes_count += 1
            generated_bytes = os.urandom(bytes_count)
            generated_int: int = int.from_bytes(bytes=generated_bytes, byteorder="big", signed=False)
            normalized_int = generated_int % diff
        return min_ + normalized_int
