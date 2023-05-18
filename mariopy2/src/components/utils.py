class Utils:

    @staticmethod
    def maprange(range_a, range_b, num):
        (a1, a2), (b1, b2) = range_a, range_b
        return  b1 + ((num - a1) * (b2 - b1) / (a2 - a1))