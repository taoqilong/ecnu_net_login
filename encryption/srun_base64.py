'''
Author       : Renjie Ji & Qilong Tao
School       : East Chine Normal University
E-mail       : renjie.ji@foxmail.com
Date         : 2023-07-15 10:17:11
Descripttion : 
version      : 
LastEditors  : Qilong Tao
LastEditTime : 2025-04-25 11:30:00
'''
import sys # Add this import at the top if not already present

_PADCHAR = "="
_ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"

def _getbyte(s, i):
    # Ensure index is within bounds before accessing
    if i >= len(s):
        # This case should ideally not be reached if imax and remainder logic is correct,
        # but adding a check prevents the IndexError directly.
        # Depending on the expected input from xencode, returning 0 or raising an error might be appropriate.
        # Returning 0 mimics some behaviors but might hide issues. Raising is safer.
        raise IndexError(f"Attempting to access index {i} in string of length {len(s)}")
        # Alternatively, consider the original JS behavior if this is a direct port.
        # return 0
    x = ord(s[i]);
    if (x > 255):
        print("INVALID_CHARACTER_ERR: DOM Exception 5")
        # Use sys.exit() for cleaner exit in scripts
        sys.exit(1) # Changed exit(0) to sys.exit(1) for error exit
    return x

def get_base64(s):
    i=0
    b10=0
    x = []
    # Calculate imax = length excluding remainder bytes
    imax = len(s) - len(s) % 3;

    if len(s) == 0:
        return s

    # Process full 3-byte chunks
    for i in range(0,imax,3):
        b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8) | _getbyte(s, i + 2);
        # Append each base64 character individually
        x.append(_ALPHA[(b10 >> 18)]);
        x.append(_ALPHA[((b10 >> 12) & 63)]);
        x.append(_ALPHA[((b10 >> 6) & 63)]);
        x.append(_ALPHA[(b10 & 63)])

    # Update i to point to the start of the remainder bytes
    i = imax
    remainder = len(s) - imax

    # Handle remainder bytes
    if remainder == 1:
        b10 = _getbyte(s, i) << 16;
        # Append characters and padding individually
        x.append(_ALPHA[(b10 >> 18)])
        x.append(_ALPHA[((b10 >> 12) & 63)])
        x.append(_PADCHAR)
        x.append(_PADCHAR)
    elif remainder == 2: # Use elif for clarity instead of else
        # Check if i+1 is a valid index before accessing
        if i + 1 < len(s):
             b10 = (_getbyte(s, i) << 16) | (_getbyte(s, i + 1) << 8);
             # Append characters and padding individually
             x.append(_ALPHA[(b10 >> 18)])
             x.append(_ALPHA[((b10 >> 12) & 63)])
             x.append(_ALPHA[((b10 >> 6) & 63)])
             x.append(_PADCHAR)
        else:
            # This case indicates an issue, as remainder is 2 but only one byte is left at index i.
            # Handle error appropriately, maybe raise an exception.
            raise ValueError(f"Logic error: Remainder is 2, but index {i+1} is out of bounds for length {len(s)}")

    # Join the list of characters into the final base64 string
    return "".join(x)

# Keep the test block if needed
if __name__ == '__main__':
    # Example usage:
    test_string_1 = "132456" # Length 6 (multiple of 3)
    test_string_2 = "13245"  # Length 5 (remainder 2)
    test_string_3 = "1324"   # Length 4 (remainder 1)
    test_string_4 = ""       # Length 0
    test_string_5 = "Man"    # Standard Base64 test

    print(f"'{test_string_1}' -> '{get_base64(test_string_1)}'")
    print(f"'{test_string_2}' -> '{get_base64(test_string_2)}'")
    print(f"'{test_string_3}' -> '{get_base64(test_string_3)}'")
    print(f"'{test_string_4}' -> '{get_base64(test_string_4)}'")
    # Note: Standard Base64 for "Man" is "TWFu". This custom function uses a different alphabet.
    print(f"'{test_string_5}' -> '{get_base64(test_string_5)}'")