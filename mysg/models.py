import random

import numpy as np
import atpy

from mysg.ranges import read_ranges, write_ranges, select_required_ranges
from mysg.util import create_dir, random_id
from mysg.parameters import write_parfile
from mysg.odict import odict

VALID = []
VALID.append(['-', 's'])
VALID.append(['-', 'p', 'a'])
VALID.append(['-', 'p', 'u'])
VALID.append(['-', 'b'])
VALID.append(['s', 'h'])
VALID.append(['-', 'm'])
VALID.append(['-', 'i'])
VALID.append(['-', 'p'])
VALID.append(['-'])
VALID.append(['-'])
VALID.append(['-'])
VALID.append(['-'])


def _check_set_name(set_name):
    for i, letter in enumerate(set_name):
        if letter not in VALID[i]:
            raise Exception("Letter %i cannot be %s" % (i + 1, letter))


def sample_set_models(set_name, number, seed=123456789):

    # Ensure reproducibility
    random.seed(seed)
    np.random.seed(seed=seed)

    # Read in the ranges
    ranges = read_ranges("models/%s/ranges.conf" % set_name)

    # Sample all values that need to be sampled
    values = atpy.Table()
    for name in ranges:
        par = ranges[name]
        if par['sampling'] == 'linear':
            values.add_column(name, np.random.uniform(par['lower'],
                                                      par['upper'],
                                                      number))
        elif par['sampling'] == 'log10':
            values.add_column(name,
                              10. ** np.random.uniform(np.log10(par['lower']),
                                                       np.log10(par['upper']),
                                                       number))
        elif par['sampling'] in ['fixed', 'str']:
            values.add_column(name, np.repeat(par['value'], number))
        elif par['sampling'] == 'linked':
            values.add_column(name, values[ranges[name]['parameter']])
        else:
            raise Exception("Unknown sampling: %s" % par['sampling'])

    # Write out parameter files
    create_dir("models/%s/par" % set_name)
    create_dir("models/%s/input" % set_name)
    create_dir("models/%s/output" % set_name)

    for i in range(len(values)):
        model_name = random_id()
        write_parfile("models/%s/par/%s.par" % (set_name, model_name), odict(zip(values.keys(), values[i])))

    # Write out table
    values.write("models/%s/parameters.hdf5" % set_name, verbose=False)


def make_set_dir(set_name, ranges_file):
    '''
    Given the name of a model set and a file containing ranges, set up the
    directory with a subset of the ranges file
    '''

    # Check set name
    _check_set_name(set_name)

    # Select ranges that are actually needed
    ranges = select_required_ranges(set_name)

    # Create directory
    create_dir('models/%s' % set_name)

    # Write out ranges file
    write_ranges('models/%s/ranges.conf' % set_name, ranges)
