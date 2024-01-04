import unittest
from array import array
from number_codec import encode, decode


def get_byte(number):
    """Takes the current number, and returns the next byte encoding it with the reminder of the number to encode. """

    number *= 256
    result = int(number)
    return result, (number - result)


class Float:
    def __init__(self):
        self.code = None

    @staticmethod
    def from_number(value) -> "Float":
        result = Float()
        result.code = array('B', encode(value)[::-1])

        return result

    def to_number(self):
        return decode(self.code[::-1])

    def __getitem__(self, index):
        return self.code[index]

    def __add__(self, other):
        if other[0] == 0:
            return self

        if self[0] == 0:
            return other

        smaller = self
        higher = other

        if smaller[0] > higher[0]:
            smaller, higher = higher, smaller

        exp_diff = higher[0] - smaller[0]

        smaller_mantissa = smaller[1:]
        smaller_mantissa[0] = smaller_mantissa[0] | 0x80
        smaller_mantissa.append(0)

        smaller_mantissa = shift_right(smaller_mantissa, exp_diff)

        b3 = higher[3] + smaller_mantissa[2]
        c3 = 1 if b3 > 255 else 0
        b3 &= 0xff

        b2 = higher[2] + smaller_mantissa[1] + c3
        c2 = 1 if b2 > 255 else 0
        b2 &= 0xff

        b1 = (higher[1] | 0x80) + smaller_mantissa[0] + c2
        c1 = 1 if b1 > 255 else 0

        exp = higher[0]
        mantissa = [b1 & 0x7f, b2, b3, 0]
        if c1:
            exp += 1
            shift_right_one(mantissa)

        result = Float()
        result.code = array('B', [exp] + mantissa[:3])

        return result


def shift_right_one(input_code):
    output = []
    carry = 0
    for b in input_code:
        new_carry = b & 1
        b >>= 1
        b |= carry << 7
        output.append(b)
        carry = new_carry
    return output


def shift_right(input_code, positions):
    code = list(input_code)
    while positions > 0:
        code = shift_right_one(code)
        positions -= 1

    return code


class TestFloat(unittest.TestCase):
    def test_zero_exponent(self):
        f = Float.from_number(0)
        self.assertEqual(0, f[0])

    def test_one_exponent(self):
        f = Float.from_number(1)
        self.assertEqual(0x81, f[0])

    def test_some_numbers(self):
        numbers = {1: [0x81, 0x00, 0x00, 0x00],
                   2: [0x82, 0x00, 0x00, 0x00],
                   0.5: [0x80, 0x00, 0x00, 0x00],
                   -128: [0x88, 0x80, 0x00, 0x00],
                   0.1: [0x7d, 0x4c, 0xcc, 0xcc]}
        for value, code in numbers.items():
            self.assertEqual(code, list(Float.from_number(value).code))

    def test_number_invariant(self):
        numbers = [1, 2, 0.5, -128]

        for number in numbers:
            self.assertEqual(number, Float.from_number(number).to_number())

    def test_shift_right(self):
        shifted = shift_right([0x80, 0x01, 0xFF, 0x00], 1)
        self.assertEqual([0x40, 0x00, 0xFF, 0x80], shifted)

        shifted = shift_right([0x80, 0x01, 0xFF, 0x00], 32)
        self.assertEqual([0x00, 0x00, 0x00, 0x00], shifted)

    def test_addition_0_1(self):
        number_1 = Float.from_number(0)
        number_2 = Float.from_number(1)
        sum_result = number_1 + number_2

        self.assertEqual(1, sum_result.to_number())

    def test_addition_2_0(self):
        number_1 = Float.from_number(2)
        number_2 = Float.from_number(0)
        sum_result = number_1 + number_2

        self.assertEqual(2, sum_result.to_number())

    def test_addition(self):
        number_1 = Float.from_number(1)
        number_2 = Float.from_number(2)
        sum = number_1 + number_2

        self.assertEqual(3, sum.to_number())
