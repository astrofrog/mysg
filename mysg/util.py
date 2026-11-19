import random
import string
import os
import shutil
import sys


def combinations(list1, list2):
    "Compute combinations of two lists of strings"
    result = []
    for item1 in list1:
        result += [item1 + item2 for item2 in list2]
    return result


def python2_hash(s):
    """
    The value that the built-in hash function returned for an ASCII string
    in Python 2 (on 64-bit platforms).

    The random seeds for the published model sets were derived from this, so
    it is needed to be able to sample the same parameters again. The hash
    function in Python 3 can't be used since it gives different values for
    strings every time Python is started.
    """
    if len(s) == 0:
        return 0
    x = ord(s[0]) << 7
    for c in s:
        x = ((1000003 * x) ^ ord(c)) & 0xFFFFFFFFFFFFFFFF
    x ^= len(s)
    if x >= 2 ** 63:
        x -= 2 ** 64
    return -2 if x == -1 else x


def random_id(length=8):
    chars = string.ascii_letters + string.digits
    # This is how random.choice picked items in Python 2, which is needed to
    # get the same model names as in the published model sets.
    return "".join(chars[int(random.random() * len(chars))]
                   for _ in range(length))


def create_dir(dir_name):
    delete_dir(dir_name)
    os.mkdir(dir_name)


def delete_dir(dir_name):
    if os.path.exists(dir_name):
        reply = input("Delete directory %s? [y/[n]] " % dir_name)
        if reply == 'y':
            shutil.rmtree(dir_name)
        else:
            print("Aborting...")
            sys.exit()
