import math


def get_byte(number):
    """Takes the current number, and returns the next byte encoding it with the reminder of the number to encode. """

    number *= 256
    result = int(number)
    return result, (number - result)


def encode(number):
    """Gets a number, returns it's encoded four bytes (memory layout, so exponent at the end)."""

    # If the number is zero, the encoding is immediate.
    # In fact, only the exponent has to be 0.
    if number == 0:
        return [0, 0, 0, 0]

    # Gets the sign from the number for later encoding
    sign = 0x80 if number < 0 else 0

    # We encode only positive numbers
    number = abs(number)

    # Shift the number so that the first fractional part bit
    # of the mantissa is 1 (0.1 binary is 0.5 decimal)
    exp = 0
    while number >= 0.5:
        number /= 2
        exp += 1
    while number < 0.5:
        number *= 2
        exp -= 1

    # Gets the three bytes encoding the mantissa
    o1, number = get_byte(number)
    o2, number = get_byte(number)
    o3, number = get_byte(number)

    # Clears the most significant bit
    # and replace it by the sign bit
    o1 &= 0x7F
    o1 |= sign

    # Encode exponent
    exp += 128

    # Returns an array (Z80 memory layout)
    return [o3, o2, o1, exp]


def decode(encoded):
    """ Takes four encoded bytes in the memory layout, and returns the decoded value. """

    # Gets the exponent
    exp = encoded[3]

    # If it's 0, we're done. The value is 0.
    if exp == 0:
        return 0

    # Extract value from the exponent
    exp -= 128

    # Extract the sign bit from MSB
    sign = encoded[2] & 0x80

    # Sets the most significant bit implied 1 in the mantissa
    encoded[2] = encoded[2] | 0x80

    # Reconstruct the mantissa
    mantissa = encoded[2]
    mantissa *= 256
    mantissa += encoded[1]
    mantissa *= 256
    mantissa += encoded[0]

    # Divide the number by the mantissa, corrected
    # by the 24 bits we just shifted while reconstructing it
    mantissa /= math.pow(2, 24 - exp)

    # Apply the sign to the whole value
    if sign:
        mantissa = -mantissa

    return mantissa


def format_code_hex(f):
    """ Formats the coded number has hexa bytes """
    return f"{f[0]:02x} {f[1]:02x} {f[2]:02x} {f[3]:02x}"


def format_code_bin(f):
    """ Formats the coded mantissa part in binary form and exponent in decimal """
    return f"{f[0]:08b} {f[1]:08b} {f[2]:08b} {f[3] - 128}"


def display_decode(encoded):
    print(f"Code : {format_code_hex(encoded)}, Value : {decode(encoded)}")


def display_code(number):
    code = encode(number)
    print(f"Code : {format_code_hex(code)}, Value : {number}")
    print(f"Code : {format_code_bin(code)}, Value : {number}")


if __name__ == '__main__':
    display_code(1)
    display_code(2)
    display_code(0.5)
    display_code(-128)
    display_code(0.1)
    display_code(0.000007)
    display_code(0.99998)
    display_code(15)
    display_code(30)

    display_decode([0x00, 0x00, 0x00, 0x80])
    display_decode([0x00, 0x00, 0x00, 0x81])
    display_decode([0x00, 0x00, 0x80, 0x88])
    display_decode([0xcc, 0xcc, 0x4c, 0x7d])
    display_decode([0xcd, 0xcc, 0x4c, 0x7d])
    display_decode([0x68, 0xb1, 0x46, 0x68])
    display_decode([0x52, 0xc7, 0x4f, 0x80])
    display_decode([0x39, 0x1c, 0x76, 0x98])
    display_decode([0x71, 0xc0, 0x47, 0x98])
    display_decode([0x00, 0x00, 0x00, 0x68])
    display_decode([0x47, 0xc0, 0x3e, 0x98])
    display_decode([0x47, 0xc0, 0x3e, 0x80])
    display_decode([0x1e, 0x01, 0x7b, 0x7e])
    display_decode([0x00, 0x00, 0x00, 0x61])
    display_decode([0xFF, 0xFF, 0x7F, 0x80])
    display_decode([0x00, 0x00, 0x72, 0x67])

    print("Sin")

    display_decode([0x83, 0xf9, 0x22, 0x7e])
    display_decode([0xd8, 0x0f, 0x49, 0x83])
    display_decode([0x00, 0x00, 0x00, 0x7f])
    display_decode([0x00, 0x00, 0x80, 0x7f])
    display_decode([0x00, 0x00, 0x80, 0x80])

    print("Tests")

    display_decode([0xFF, 0xFF, 0x7F, 0x77])
    display_decode([0x00, 0x00, 0x10, 0x84])

