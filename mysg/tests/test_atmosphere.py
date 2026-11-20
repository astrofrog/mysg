import os
import shutil

import numpy as np
import pytest
from astropy.table import Table

from mysg.atmosphere import (BUNDLED_DIR, DEFAULT_ATMOSPHERES, PHOENIX_FLUX_SCALE, interp_atmos,
                             phoenix_table, solar_phoenix_table, table_sha256)


def bundled(family, temperature):
    prefix = family[0] + 't'
    return Table.read(os.path.join(BUNDLED_DIR, family, '{0}{1:05d}g+4.0z-2.0.hdf5'.format(prefix, temperature)),
                      path='Table')


@pytest.mark.parametrize(('family', 't1', 't2'), [('phoenix', 3000, 3100), ('kurucz', 5000, 5250)])
def test_r17(family, t1, t2):

    # The 'r17' set is the bundled one: the spectrum at a tabulated temperature is the table, and half way
    # between two temperatures it is the mean of the two tables.

    table1, table2 = bundled(family, t1), bundled(family, t2)

    nu, fnu = interp_atmos(float(t2), atmospheres='r17')
    np.testing.assert_array_equal(nu, table1['nu'])
    np.testing.assert_array_equal(fnu, table2['fnu'])

    nu, fnu = interp_atmos(0.5 * (t1 + t2), atmospheres='r17')
    np.testing.assert_array_equal(fnu, 0.5 * table1['fnu'] + 0.5 * table2['fnu'])


def test_directory(tmp_path):

    # A directory with phoenix/ and kurucz/ sub-directories gives the same spectra as the same tables in
    # the bundled set.

    for family, temperatures in (('phoenix', (3000, 3100)), ('kurucz', (5000, 5250))):
        os.mkdir(tmp_path / family)
        for temperature in temperatures:
            name = '{0}t{1:05d}g+4.0z-2.0.hdf5'.format(family[0], temperature)
            shutil.copy(os.path.join(BUNDLED_DIR, family, name), tmp_path / family / name)

    for temperature in (3040., 5100.):
        nu, fnu = interp_atmos(temperature, atmospheres=str(tmp_path))
        nu_r17, fnu_r17 = interp_atmos(temperature, atmospheres='r17')
        np.testing.assert_array_equal(nu, nu_r17)
        np.testing.assert_array_equal(fnu, fnu_r17)


def test_invalid():
    with pytest.raises(ValueError, match="atmospheres should be"):
        interp_atmos(3000., atmospheres='not-a-set')


def test_phoenix_table():

    # Format of the PHOENIX tables: increasing frequency, wavelength in microns, extra point at 1 cm

    lam = np.array([1000., 2000., 4000.])
    fnu = np.array([1., 2., 3.])
    table = phoenix_table(lam, fnu, 0.5)
    assert table.dtype.names == ('wav', 'nu', 'fnu')
    assert np.all(np.diff(table['nu']) > 0)
    np.testing.assert_allclose(table['wav'], [1e4, 0.4, 0.2, 0.1])
    np.testing.assert_allclose(table['nu'] * table['wav'], 2.99792458e14)
    np.testing.assert_array_equal(table['fnu'], [0.5, 3. * PHOENIX_FLUX_SCALE, 2. * PHOENIX_FLUX_SCALE,
                                                 1. * PHOENIX_FLUX_SCALE])
    assert len(table_sha256(table)) == 64


def test_solar():

    # Downloads two spectra from the STScI archive (11 MB each). solar_phoenix_table checks the tables
    # against the SHA-256 of the R24 v1.3 tables.

    assert DEFAULT_ATMOSPHERES == 'solar'

    table1, table2 = solar_phoenix_table(3000), solar_phoenix_table(3100)
    assert len(table1) == 103001

    nu, fnu = interp_atmos(3050.)
    np.testing.assert_array_equal(nu, table1['nu'])
    np.testing.assert_array_equal(fnu, 0.5 * table1['fnu'] + 0.5 * table2['fnu'])

    # Above 4000 K the solar set uses the bundled Kurucz tables
    nu, fnu = interp_atmos(5000.)
    np.testing.assert_array_equal(fnu, bundled('kurucz', 5000)['fnu'])
