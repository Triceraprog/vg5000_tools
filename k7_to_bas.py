"""
Small utility to convert VG5000µ k7 files containing BASIC programs to the actual BASIC listing.

Written for Triceraprog by Sylvain Glaize.
"""

# Enter the filename of the VG5000µ K7 file you want to decode
filename = "filename.k7"


def two_bytes_to_num(b):
    """ Function to decode 16 bits numbers """
    return b[1] * 256 + b[0]


def print_header(header):
    """ Print the header of the program """
    print("-" * 40)
    print("Format: " + str(header[10]))
    print("Name: " + bytes(header[11:17]).decode('ascii'))
    print("Version: " + str(header[17]))
    print("Start Line: " + str(header[18:23]))
    print("Protection: " + str(header[23]))
    print("Check Pos.: " + str(header[24:26]))
    print("Start Adr.: " + hex(two_bytes_to_num(header[26:28])))
    print("Data Length: " + str(two_bytes_to_num(header[28:30])))
    print("Check: " + str(header[30:32]))


# List of the BASIC tokens and their names
tokens = {128: 'END', 129: 'FOR', 130: 'NEXT', 131: 'DATA', 132: 'INPUT', 133: 'DIM', 134: 'READ', 135: 'LET',
          136: 'GOTO', 137: 'RUN', 138: 'IF', 139: 'RESTORE', 140: 'GOSUB', 141: 'RETURN', 142: 'REM', 143: 'STOP',
          144: 'ON', 145: 'LPRINT', 146: 'DEF', 147: 'POKE', 148: 'PRINT', 149: 'CONT', 150: 'LIST', 151: 'LLIST',
          152: 'CLEAR', 153: 'RENUM', 154: 'AUTO', 155: 'LOAD', 156: 'SAVE', 157: 'CLOAD', 158: 'CSAVE', 159: 'CALL',
          160: 'INIT', 161: 'SOUND', 162: 'PLAY', 163: 'TX', 164: 'GR', 165: 'SCREEN', 166: 'DISPLAY', 167: 'STORE',
          168: 'SCROLL', 169: 'PAGE', 170: 'DELIM', 171: 'SETE', 172: 'ET', 173: 'EG', 174: 'CURSOR', 175: 'DISK',
          176: 'MODEM', 177: 'NEW', 178: 'TAB(', 179: 'TO', 180: 'FN', 181: 'SPC(', 182: 'THEN', 183: 'NOT',
          184: 'STEP', 185: '+', 186: '-', 187: '*', 188: '/', 189: '^', 190: 'AND', 191: 'OR', 192: '>',
          193: '=', 194: '<', 195: 'SGN', 196: 'INT', 197: 'ABS', 198: 'USR', 199: 'FRE', 200: 'LPOS', 201: 'POS',
          202: 'SQR', 203: 'RND', 204: 'LOG', 205: 'EXP', 206: 'COS', 207: 'SIN', 208: 'TAN', 209: 'ATN', 210: 'PEEK',
          211: 'LEN', 212: 'STR$', 213: 'VAL', 214: 'ASC', 215: 'STICKX', 216: 'STICKY', 217: 'ACTION', 218: 'KEY',
          219: 'LPEN', 220: 'CHR$', 221: 'LEFT$', 222: 'RIGHT$', 223: 'MID$'}


# Accentuated characters are encoded in the lower part of the "ASCII" table on VG5000µ
accents = "îéùïçûàâèôê£½"
accents_count = len(accents)

with open(filename, "rb") as w:
    content = w.read()


# The utility will convert K7 files containing several programs
while len(content):
    # The header if marked with a series of 0xd3. Stop immediately if not found.
    if content[0] != 0xd3:
        print("Incorrect format")
        exit(1)

    # In case there's not enough data to have a valid program, the programs also stops
    if len(content) < 32:
        exit(1)

    print_header(content)

    data_length = two_bytes_to_num(content[28:30])

    # 0xd6 marks the beginning of the payload. In fact, it's always at the same relative position,
    # the find() call comes from an earlier version of the script.
    first_d6 = content.find(0xd6)

    # There are 10 times 0xd6. Skip them.
    content = content[first_d6 + 10:]

    total_decoded_count = 0
    while len(content) >= 4:
        # The two first bytes of a line is the line number
        line_number = content[3] * 256 + content[2]

        # The two bytes after the line number is the memory link to the next line. It's probably
        # invalid and will be recomputed after being loaded. It's saved nevertheless, as saving a BASIC
        # program just dumps the memory content of the TEXT part, so we skip it.
        content = content[4:]

        # Line 0 means the last line of the program has been reached. Skip the content to the next 0xd3
        if line_number == 0:
            next_program = content.find(0xd3)
            if next_program != -1:
                content = content[next_program:]
                break
            else:
                continue

        # Prepare decoding
        decoded = ""
        number = 0
        decoded_count = 0
        number_acc = []
        parsing = True

        # Decode until the expected data length is reached
        while parsing and total_decoded_count < data_length:
            c = content[decoded_count]
            decoded_count += 1

            if number:
                # Decoding specific 2 bytes integers
                number_acc.append(c)
                number -= 1
                if number == 0:
                    decoded_number = number_acc[0] + number_acc[1] * 256
                    decoded += " " + str(decoded_number)
                    number_acc = []
            else:
                if c == 0:
                    parsing = False         # Line is finished
                elif c in tokens:
                    decoded += tokens[c]    # Found a token
                elif c == 0x0e:
                    number = 2              # Found a specific 2 bytes integer (comes after GOTO, GOSUB, RESTORE)
                else:
                    if 17 <= c <= 17 + accents_count:
                        decoded += accents[c - 17]      # Found a special character
                    else:
                        decoded += bytes([c]).decode('ascii')   # Found an ASCII character

        total_decoded_count += decoded_count + 4
        print(str(line_number) + " " + str(decoded))

        content = content[decoded_count:]
