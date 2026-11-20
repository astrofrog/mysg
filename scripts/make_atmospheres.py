"""Build a directory of mysg stellar-atmosphere tables.

    python scripts/make_atmospheres.py solar OUTDIR
    python scripts/make_atmospheres.py MH OUTDIR [--cache DIR] [--record]

Both write

    OUTDIR/phoenix/pt{T:05d}g+4.0z{MH:+.1f}.hdf5   T = 2000-4000 K in steps of 100 K
    OUTDIR/kurucz/kt{T:05d}g+4.0z{MH:+.1f}.hdf5    the 65 temperatures of the bundled Kurucz set

for use with ``setup_model(..., atmospheres=OUTDIR)`` or ``interp_atmos(T, atmospheres=OUTDIR)``.
Unlike the bundled files, the ``z`` in these names is the [M/H] of both families. All spectra have
log g = 4.0. See mysg/data/README.md for the sources and checks.

``solar`` writes the default set of mysg ('solar', used for the R24 v1.3 models), for use without
network access: the PHOENIX tables of mysg.atmosphere.solar_phoenix_table (built from the STScI
phoenixm00 spectra and checked against the R24 v1.3 checksums) and copies of the bundled Kurucz tables.

MH (e.g. -0.5) writes a set with [M/H] = MH at every temperature and scaled-solar abundances:

* PHOENIX (T < 4000 K): BT-Settl with the Asplund et al. (2009) abundances (Allard et al. 2012,
  "BT-Settl AGSS2009") from the SVO Theory service (model bt-settl-agss, alpha = 0), resampled with
  flux conservation onto the wavelength grid of the STScI phoenixm00 files (103,000 points from
  12.6 Angstrom to 77.6 micron), and converted as the solar tables (mysg.atmosphere.phoenix_table: not
  normalized). The point at 1 cm continues the spectrum from 77.6 micron with the Rayleigh-Jeans slope,
  F_nu ~ lambda^-2.
* Kurucz (T >= 4000 K): Castelli & Kurucz (2004) ATLAS9 models, STScI CDBS
  grid/ck04models/ck{tag}/ck{tag}_{T}.fits (tags m25 ... m05, p00, p02, p05), column g40, converted as
  the bundled files: one point at 1 cm extrapolated in log-log space from the last two points, columns
  ``nu`` and ``fnu`` with increasing frequency, normalized so that the integral of fnu over frequency is
  1.

The SHA-256 of each table and downloaded spectrum is compared with the values in
atmospheres_sha256.json (next to this script); --record stores them there instead. Downloads are cached
in --cache (default OUTDIR/download).
"""
import argparse
import hashlib
import io
import json
import os
import urllib.request

import h5py
import numpy as np
from astropy.io.votable import parse_single_table
from scipy.integrate import trapezoid

from mysg.atmosphere import (BUNDLED_DIR, C_ANGSTROM, LAM_1CM, PHOENIX_FLUX_SCALE, list_atmospheres,
                             phoenix_table, read_cdbs_spectrum, solar_phoenix_table, table_sha256)

CDBS = 'https://archive.stsci.edu/hlsps/reference-atlases/cdbs/grid'
SVO = 'https://svo2.cab.inta-csic.es/theory/newov2/ssap.php'
CHECKSUMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'atmospheres_sha256.json')
T_PHOENIX = np.arange(2000, 4001, 100)


def file_sha256(path):
    with open(path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def download(url, path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        urllib.request.urlretrieve(url, path + '.part')
        os.replace(path + '.part', path)
    return path


def svo_bt_settl(teff, mh, cache):
    """Path of the BT-Settl AGSS2009 spectrum with this Teff, log g = 4.0, [M/H] = mh and alpha = 0 from
    the SVO Theory service (downloaded if not in the cache), and its wavelengths (Angstrom, increasing)
    and fluxes per unit wavelength."""
    path = os.path.join(cache, 'svo_bt-settl-agss', f'bt-settl-agss_{teff:05d}_g4.0_m{mh:+.1f}_a+0.0.txt')
    if not os.path.exists(path):
        query = (f'{SVO}?model=bt-settl-agss&teff_min={teff}&teff_max={teff}&logg_min=4&logg_max=4'
                 f'&meta_min={mh}&meta_max={mh}&REQUEST=queryData')
        with urllib.request.urlopen(query) as response:
            table = parse_single_table(io.BytesIO(response.read())).to_table()
        rows = table[np.isclose(table['alpha'], 0.) & np.isclose(table['meta'], mh)
                     & np.isclose(table['teff'], teff) & np.isclose(table['logg'], 4.)]
        if len(rows) != 1:
            raise ValueError(f'SVO bt-settl-agss: {len(rows)} spectra for Teff = {teff}, log g = 4, '
                             f'[M/H] = {mh}, alpha = 0')
        download(str(rows['Access.Reference'][0]) + '&format=ascii', path)
    header = {}
    with open(path) as f:
        for line in f:
            if not line.startswith('#'):
                break
            if '=' in line:
                key, value = line[1:].split('=', 1)
                header[key.strip()] = float(value.split()[0])
    expected = {'teff': teff, 'logg': 4., 'meta': mh, 'alpha': 0.}
    if any(not np.isclose(header.get(k, np.nan), v) for k, v in expected.items()):
        raise ValueError(f'{path}: header {header} does not match {expected}')
    lam, flam = np.loadtxt(path, unpack=True)
    order = np.argsort(lam, kind='stable')
    lam, flam = lam[order], flam[order]
    keep = np.concatenate([[True], np.diff(lam) > 0])
    return path, lam[keep], flam[keep]


def rebin(lam, flam, lam_new):
    """Mean of flam over the bins centred on lam_new (edges at the geometric midpoints), from the
    trapezoid integral of the input spectrum: conserves the flux in each bin."""
    mid = np.sqrt(lam_new[1:] * lam_new[:-1])
    edges = np.concatenate([[lam_new[0] ** 2 / mid[0]], mid, [lam_new[-1] ** 2 / mid[-1]]])
    if edges[0] < lam[0] or edges[-1] > lam[-1]:
        raise ValueError('the input spectrum does not cover the output wavelength grid')
    cumulative = np.concatenate([[0.], np.cumsum(0.5 * (flam[1:] + flam[:-1]) * np.diff(lam))])
    return np.diff(np.interp(edges, lam, cumulative)) / np.diff(edges)


def kurucz_table(lam, fnu):
    slope = np.log10(fnu[-1] / fnu[-2]) / np.log10(lam[-1] / lam[-2])
    f_extra = fnu[-1] * (LAM_1CM / lam[-1]) ** slope
    lam = np.append(lam, LAM_1CM)
    fnu = np.append(fnu, f_extra)
    table = np.zeros(len(lam), dtype=[('nu', '<f8'), ('fnu', '<f8')])
    table['nu'] = (C_ANGSTROM / lam)[::-1]
    table['fnu'] = fnu[::-1]
    table['fnu'] /= trapezoid(table['fnu'], table['nu'])
    return table


class Writer:
    """Writes the tables of one set and collects the SHA-256 of the tables and of the source spectra."""

    def __init__(self, outdir, mh, cache):
        self.outdir, self.mh, self.cache = outdir, mh, cache
        self.tables, self.sources = {}, {}
        for family in ('phoenix', 'kurucz'):
            os.makedirs(os.path.join(outdir, family), exist_ok=True)

    def write(self, family, temp, table):
        name = f'{family}/{family[0]}t{int(temp):05d}g+4.0z{self.mh:+.1f}.hdf5'
        with h5py.File(os.path.join(self.outdir, name), 'w') as f:
            f['Table'] = table
        self.tables[name] = table_sha256(table)

    def source(self, path):
        self.sources[os.path.relpath(path, self.cache)] = file_sha256(path)
        return path


def build_solar(writer):
    for temp in T_PHOENIX:
        writer.write('phoenix', temp, np.asarray(solar_phoenix_table(int(temp))))
    print(f'{len(T_PHOENIX)} phoenix tables (STScI phoenixm00, identical to the R24 v1.3 tables)')
    teff, models = list_atmospheres(os.path.join(BUNDLED_DIR, 'kurucz'))
    for temp, model in zip(teff, models):
        with h5py.File(model, 'r') as f:
            writer.write('kurucz', temp, f['Table'][:])
    print(f'{len(teff)} kurucz tables (copies of the bundled tables)')


def build_mh(writer):
    mh, cache = writer.mh, writer.cache
    relpath = 'phoenix/phoenixm00/phoenixm00_3000.fits'
    lam_grid, _ = read_cdbs_spectrum(writer.source(download(f'{CDBS}/{relpath}',
                                                            os.path.join(cache, 'cdbs', relpath))))
    for temp in T_PHOENIX:
        path, lam, flam = svo_bt_settl(int(temp), mh, cache)
        writer.source(path)
        fnu = rebin(lam, flam, lam_grid) * (lam_grid ** 2 / C_ANGSTROM)
        fnu_1cm = fnu[-1] * PHOENIX_FLUX_SCALE * (LAM_1CM / lam_grid[-1]) ** -2.
        writer.write('phoenix', temp, phoenix_table(lam_grid, fnu, fnu_1cm))
    print(f'[M/H] = {mh:+.1f}: {len(T_PHOENIX)} phoenix tables (SVO bt-settl-agss, alpha = 0)')
    tag = 'p00' if mh == 0 else ('p' if mh > 0 else 'm') + f'{round(abs(mh) * 10):02d}'
    teff, _ = list_atmospheres(os.path.join(BUNDLED_DIR, 'kurucz'))
    for temp in teff.astype(int):
        relpath = f'ck04models/ck{tag}/ck{tag}_{temp}.fits'
        lam, flam = read_cdbs_spectrum(writer.source(download(f'{CDBS}/{relpath}',
                                                              os.path.join(cache, 'cdbs', relpath))))
        writer.write('kurucz', temp, kurucz_table(lam, flam * (lam ** 2 / C_ANGSTROM)))
    print(f'[M/H] = {mh:+.1f}: {len(teff)} kurucz tables (CDBS ck04models/ck{tag})')


def check(writer, key, record):
    """Compare the checksums with the recorded ones, or record them."""
    recorded = {}
    if os.path.exists(CHECKSUMS):
        with open(CHECKSUMS) as f:
            recorded = json.load(f)
    if record:
        recorded[key] = {'tables': writer.tables, 'sources': writer.sources}
        with open(CHECKSUMS, 'w') as f:
            json.dump(recorded, f, indent=1, sort_keys=True)
            f.write('\n')
        print(f'Recorded the checksums of set {key} in {CHECKSUMS}')
        return
    if key not in recorded:
        print(f'No recorded checksums for set {key} in {CHECKSUMS}')
        return
    for kind, values in (('tables', writer.tables), ('sources', writer.sources)):
        if not values:
            continue
        expected = recorded[key][kind]
        differ = sorted(name for name in values if expected.get(name) != values[name])
        print(f'{kind}: {len(values) - len(differ)} of {len(values)} match the recorded SHA-256'
              + (': differ for ' + ', '.join(differ) if differ else ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('set', help="'solar' or [M/H], e.g. -0.5")
    parser.add_argument('outdir')
    parser.add_argument('--cache', help='directory for the downloaded spectra (default OUTDIR/download)')
    parser.add_argument('--record', action='store_true',
                        help='store the checksums in atmospheres_sha256.json instead of comparing them')
    args = parser.parse_args()
    if args.set == 'solar':
        writer = Writer(args.outdir, 0., None)
        build_solar(writer)
        key = 'solar'
    else:
        writer = Writer(args.outdir, float(args.set), args.cache or os.path.join(args.outdir, 'download'))
        build_mh(writer)
        key = f'{writer.mh:+.1f}'
    check(writer, key, args.record)


if __name__ == '__main__':
    main()
