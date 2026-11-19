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


def random_id(length=8):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


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
