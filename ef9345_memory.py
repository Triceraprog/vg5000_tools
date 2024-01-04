class InvalidTriplet(Exception):
    pass


def verify_triplet(x, y, z):
    if x > 39 or x < 0:
        raise InvalidTriplet()
    if y < 0 or y > 31 or y in (2, 3, 4, 5, 6, 7):
        raise InvalidTriplet()
    if z < 0 or z > 15:
        raise InvalidTriplet()


def triplet_to_main_pointer(x, y, z):
    verify_triplet(x, y, z)

    z_b_0 = 1 if z & 1 else 0
    z_b_1 = 1 if z & 2 else 0
    z_d_0 = 1 if z & 4 else 0
    z_d_1 = 1 if z & 8 else 0

    r6 = y
    r7 = x

    r6 |= z_d_0 << 5 | z_d_1 << 7
    r7 |= z_b_1 << 6 | z_b_0 << 7

    return r6, r7


def triplet_to_aux_pointer(x, y, z):
    verify_triplet(x, y, z)

    z_bp_0 = 1 if z & 1 else 0
    z_bp_1 = 1 if z & 2 else 0
    z_dp_0 = 1 if z & 4 else 0
    z_dp_1 = 1 if z & 8 else 0

    if z_dp_1:
        print("Only 8k address supported")
        exit(1)

    r4 = y
    r5 = x

    r4 |= z_dp_0 << 5
    r5 |= z_bp_1 << 6 | z_bp_0 << 7

    return r4, r5


def format_pointer(first_reg, second_reg):
    return f"0x{first_reg:02x}{second_reg:02x}"


def triplet_to_physical_address(x, y, z):
    verify_triplet(x, y, z)

    address = x & 7
    address |= (z & 14) << 11

    if y >= 8:
        if not x & (1 << 5):
            address |= (z & 1) << 11  # b0
            address |= (y & 31) << 5 # Y
            address |= (x & 12) << 3 # X4,X3
        else:
            address |= (z & 1) << 11  # b0
            address |= (y & 7) << 5  # low Y
            address |= (y & 24) << 3  # high Y
    else:  # y < 8
        if not y & 1:  # => Y = 1
            address |= (z & 1) << 11  # b0
            address |= (x & 56) << 5 # high X
        elif not z & 1:  # b0
            address |= (x & (1 << 3)) << 10  # X3

            not_x4 = 0 if x & 16 else 1
            not_x5 = 0 if x & 32 else 1
            address |= not_x4 << 6
            address |= not_x4 << 5
        else:
            address |= (x & (1 << 3)) << 10  # X3

            not_x4 = 0 if x & 16 else 1
            not_x5 = 0 if x & 32 else 1
            address |= not_x4 << 6
            address |= not_x4 << 5

    return address


addresses = [
        (0, 0, 0),  # Iterating on Z
        (0, 0, 1),
        (0, 0, 2),
        (0, 0, 3),
        (0, 0, 0),  # Iterating on X
        (1, 0, 0),
        (2, 0, 0),
        (3, 0, 0),
        (0, 0, 0),  # Iterating on Y
        (0, 1, 0),
        (0, 8, 0),
        (0, 9, 0),
        ]

print("Triplet       MAIN     AUX   PHYS.")
for adr in addresses:
    main_p = triplet_to_main_pointer(*adr)
    aux_p = triplet_to_aux_pointer(*adr)

    format_main = format_pointer(*main_p)
    format_aux = format_pointer(*aux_p)

    physical_ptr = triplet_to_physical_address(*adr)

    print(f"{adr} : {format_main}  {format_aux}  0x{physical_ptr:04x}")

characters = [0, 1, 2, 3, 32, 33, 34, 35, 36, 124, 125, 126, 127]


def char_to_local_shift_addr(c):
    x = c & 3
    y = (c & 0b1111100) >> 2
    z = 0

    return x, y, z


for z in [3, 4, 5, 6, 7]:
    for c in characters:
        triplet = char_to_local_shift_addr(c)
        x, y, zp = triplet
        triplet = (x, y, z)

        aux_p = triplet_to_aux_pointer(*triplet)
        format_addr = format_pointer(*aux_p)

        triplet_end = (x + (9 << 2), y, z)
        aux_p_end = triplet_to_aux_pointer(*triplet_end)
        format_addr_end = format_pointer(*aux_p_end)

        physical_ptr = triplet_to_physical_address(*triplet)
        physical_ptr_end = triplet_to_physical_address(*triplet_end)

        print(f"{c:3} : {repr(triplet):>15s}  {format_addr} to {format_addr_end}  0x{physical_ptr:04x} to 0x{physical_ptr_end:04x}")


# On pourrait faire une petite app interactive qui montre la mémoire logique et la mémoire physique
# À partir d'une configuration (DOR), on clique sur "montrer l'écran", une ligne particulière, un emplacement particulier à l'écran.
# On peut montrer l'emplacement d'un charset, et d'un char particulier avec un charset particulier

