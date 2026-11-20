import glob
import hashlib
import json
import os
from functools import lru_cache

import numpy as np
from astropy.io import fits
from astropy.table import Table
from astropy.utils.data import download_file

# Set path with atmosphere templates
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')

# The PHOENIX atmospheres are used below this temperature, the Kurucz atmospheres at and above it
T_SWITCH = 4000.

# Set of atmospheres used when none is given (see data/README.md):
#   'solar' : solar metallicity at all temperatures, as for the R24 v1.3 models. The PHOENIX tables are
#             built on first use from spectra downloaded from the STScI archive (see solar_phoenix_table)
#   'r17'   : the bundled set used for the R17 models and the R24 models before v1.3, which has
#             [M/H] = -2 below 4000 K and solar metallicity above
DEFAULT_ATMOSPHERES = 'solar'

# Bundled atmospheres (the 'r17' set; its Kurucz tables are also those of the 'solar' set)
BUNDLED_DIR = os.path.join(DATA_PATH, 'atmos')

# Source, 1 cm points and checksums of the solar PHOENIX tables
with open(os.path.join(DATA_PATH, 'phoenix_solar.json')) as f:
    PHOENIX_SOLAR = json.load(f)

# The unit conversions use the values that astropy.units gives, with which the R24 v1.3 tables were
# made, so that solar_phoenix_table reproduces those tables bit for bit.
C_ANGSTROM = 2.9979245799999995e18  # speed of light in Angstrom / s
ANGSTROM_MICRON = 0.00010000000000000002  # 1 Angstrom in micron
ARCSEC2_SR = (np.pi / 180. / 3600.) ** 2  # 1 arcsec^2 in sr
PHOENIX_FLUX_SCALE = np.pi ** 2 * ARCSEC2_SR / 2.  # factor applied to F_nu in the PHOENIX tables
LAM_1CM = 1e8  # wavelength of the extra point at the end of each PHOENIX table (Angstrom)


def table_sha256(table):
    """SHA-256 of the values in a table, independent of the file format: the rows as little-endian
    64-bit floats, with the columns in the order of the table."""
    array = np.asarray(table)
    dtype = [(name, '<f8') for name in array.dtype.names]
    return hashlib.sha256(np.ascontiguousarray(array.astype(dtype)).tobytes()).hexdigest()


def read_cdbs_spectrum(filename, column='g40'):
    """Wavelength (Angstrom) and flux per unit wavelength in one column of a STScI CDBS grid file
    (column g40 is the spectrum with log g = 4.0)."""
    with fits.open(filename) as hdulist:
        data = hdulist[1].data
        lam = np.array(data['WAVELENGTH'], dtype=float)
        flam = np.array(data[column], dtype=float)
    if not np.any(flam > 0):
        raise ValueError("{0}: column {1} has no positive fluxes".format(filename, column))
    return lam, flam


def phoenix_table(lam, fnu, fnu_1cm):
    """
    PHOENIX table in the format of the R24 v1.3 tables: columns wav (micron), nu (Hz) and fnu, with
    increasing frequency, where fnu is the flux per unit frequency at the stellar surface
    (erg/s/cm^2/Hz) times PHOENIX_FLUX_SCALE, so the table is not normalized. One point is added at a
    wavelength of 1 cm, where the flux is fnu_1cm (which includes PHOENIX_FLUX_SCALE).

    lam : wavelengths (Angstrom, increasing)
    fnu : flux per unit frequency at these wavelengths (erg/s/cm^2/Hz)
    """
    lam = np.append(lam, LAM_1CM)
    table = np.zeros(len(lam), dtype=[('wav', '<f8'), ('nu', '<f8'), ('fnu', '<f8')])
    table['wav'] = lam * ANGSTROM_MICRON
    table['nu'] = C_ANGSTROM / lam
    table['fnu'][:-1] = fnu * PHOENIX_FLUX_SCALE
    table['fnu'][-1] = fnu_1cm
    return table[::-1]


@lru_cache(maxsize=None)
def solar_phoenix_table(teff):
    """
    Solar-metallicity PHOENIX table for the effective temperature teff (2000 to 4000 K in steps of 100 K),
    as used for the R24 v1.3 models (T. Richardson 2026, see data/README.md).

    The spectrum (BT-Settl, [M/H] = 0, log g = 4.0) is downloaded from the STScI archive on first use
    and cached by astropy (by default in ~/.mysg/cache). The flux at 1 cm is the recorded value, and the
    table is checked against the recorded SHA-256 of the R24 v1.3 table.
    """
    entry = PHOENIX_SOLAR['tables'][str(int(teff))]
    filename = download_file(PHOENIX_SOLAR['url'].format(teff=int(teff)), cache=True, pkgname='mysg')
    lam, flam = read_cdbs_spectrum(filename, PHOENIX_SOLAR['column'])
    table = phoenix_table(lam, flam * (lam ** 2 / C_ANGSTROM), entry['fnu_1cm'])
    if table_sha256(table) != entry['sha256']:
        raise ValueError("The table built from {0} differs from the R24 v1.3 table for {1} K (SHA-256 {2}, "
                         "expected {3})".format(filename, teff, table_sha256(table), entry['sha256']))
    return Table(table)


@lru_cache(maxsize=None)
def read_atmosphere(filename):
    return Table.read(filename, path="Table")


@lru_cache(maxsize=None)
def list_atmospheres(directory):
    """Effective temperatures (sorted) and names of the atmosphere tables in a directory. The temperature
    is read from characters 2-7 of the file names, e.g. pt02000g+4.0z-2.0.hdf5."""
    models = glob.glob(os.path.join(directory, '*.hdf5'))
    if not models:
        raise FileNotFoundError("No atmosphere tables (*.hdf5) in {0}".format(directory))
    teff = np.array([os.path.basename(model)[2:7] for model in models], dtype=np.float32)
    order = np.argsort(teff)
    return teff[order], [models[i] for i in order]


def atmosphere_tables(family, atmospheres=None):
    """
    Effective temperatures (sorted) of the tables of one family ('phoenix' or 'kurucz') in a set of
    atmospheres, and a function that returns the table with a given index.

    atmospheres : 'solar', 'r17' or a directory with 'phoenix' and 'kurucz' sub-directories of tables in
        the format of the bundled ones (default: DEFAULT_ATMOSPHERES)
    """
    if atmospheres is None:
        atmospheres = DEFAULT_ATMOSPHERES
    if atmospheres == 'solar' and family == 'phoenix':
        teff = np.array(sorted(PHOENIX_SOLAR['tables'], key=float), dtype=np.float32)
        return teff, lambda i: solar_phoenix_table(int(teff[i]))
    if atmospheres in ('solar', 'r17'):
        directory = BUNDLED_DIR
    elif os.path.isdir(atmospheres):
        directory = atmospheres
    else:
        raise ValueError("atmospheres should be 'solar', 'r17' or a directory, not {0!r}".format(atmospheres))
    teff, models = list_atmospheres(os.path.join(os.path.abspath(directory), family))
    return teff, lambda i: read_atmosphere(models[i])


def interp_atmos(tval, atmospheres=None):
    """
    Spectrum (nu, fnu) of a star with effective temperature tval, interpolated linearly between the two
    closest tables of the PHOENIX (below T_SWITCH) or Kurucz family.

    atmospheres : 'solar', 'r17' or a directory of tables (see atmosphere_tables and data/README.md;
        default: DEFAULT_ATMOSPHERES)
    """

    # Decide which set of atmospheres to use
    family = 'phoenix' if tval < T_SWITCH else 'kurucz'
    teff, table = atmosphere_tables(family, atmospheres)

    # Locate the temperature in the array
    i = np.searchsorted(teff, tval)

    # Retrieve two neighboring tables
    t1, t2 = table(i - 1), table(i)

    # Compute the interpolation fraction
    frac = (tval - teff[i - 1]) / (teff[i] - teff[i - 1])

    # Interpolate and return on the fly
    return t1['nu'], t1['fnu'] * (1. - frac) + t2['fnu'] * frac
