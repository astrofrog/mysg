# Where did the data come from?

The stellar photosphere models for the central sources come in sets. Each
set has PHOENIX models, used for T < 4000 K, and Kurucz models, used for
T >= 4000 K, and the spectrum for a given temperature is found by linear
interpolation between the two closest models. All models have log g = 4.0.
``setup_model`` and ``interp_atmos`` take the set as the ``atmospheres``
option:

* ``'solar'`` (the default since version 1.3): solar metallicity at all
  temperatures, as used for version 1.3 of the R24 models (the model grid
  of T. Richardson et al., made with mysg). The PHOENIX tables are made
  from spectra downloaded from the STScI archive the first time they are
  needed (see "Solar PHOENIX" below), and the Kurucz tables are the bundled
  ones.
* ``'r17'``: the bundled set in the ``atmos`` directory, used for the R17
  models (Robitaille 2017) and for the R24 models before v1.3.
* a directory with ``phoenix/`` and ``kurucz/`` sub-directories of tables
  in the same format, such as the sets with one metallicity written by
  ``scripts/make_atmospheres.py`` (see the last section).

Each file contains a table with the frequency (``nu``, in Hz) and the flux
per unit frequency (``fnu``). The bundled tables are normalized so that the
integral of the flux over frequency is 1, while the solar PHOENIX tables are
not (see below). The PHOENIX files also contain the wavelength (``wav``, in
microns).

Note that the two families of the bundled ``'r17'`` set do not have the same
metallicity: the PHOENIX models have [M/H] = -2 (1/100 solar) and the Kurucz
models have solar metallicity, even though the file names of both contain
``z-2.0`` (see below). The stellar spectra of that set therefore change
metallicity at 4000 K.

## PHOENIX with [M/H] = -2 (the ``'r17'`` set)

The files in ``atmos/phoenix/`` are named
``pt{temperature:05d}g+4.0z-2.0.hdf5`` and cover 2000 to 4000 K in steps of
100 K. They are PHOENIX models from the grid computed for the Gaia mission
(Brott & Hauschildt 2005), with [M/H] = -2.0 and no alpha enhancement. For
these files, the ``z-2.0`` in the name is the PHOENIX [M/H]. The paper
describes models with T >= 2700 K and spectra sampled every 2 Angstrom, while
the files used here are from a later, higher resolution version of the grid
that extends down to 2000 K.

The original spectra are the high-resolution files (sampled every 0.02
Angstrom in the optical) named

    lte{temperature/100}-4.0-2.0.Cond.PHOENIX2004.tab.7.gz

which were downloaded in 2010 from

    ftp://ftp.hs.uni-hamburg.de/pub/outgoing/phoenix/GAIA_HighRes/Spectra/

In PHOENIX file names the sign of log g is reversed, so ``-4.0`` means
log g = +4.0, while ``-2.0`` is [M/H]. As of November 2026 the files for
T >= 3000 K are in the ``Z-2.0a+0.0`` sub-directory, and the files for
cooler models are no longer publicly available there.

Each spectrum was rebinned as follows:

* The flux per unit frequency was averaged over 1000 bins equally spaced in
  log wavelength between 10^-1.5 and 10^2.8 microns (0.03 to 630 microns).
  The average was computed by integrating the flux over each bin, using
  interpolation in log-log space, and dividing by the width of the bin in
  frequency, so the rebinning conserves flux.
* One point was added at a wavelength of 1 cm by extrapolating in log-log
  space.
* The spectrum was normalized so that its integral over frequency is 1.

Models with [M/H] = -2 were used because, when the files were downloaded, the
status page for the grid listed the solar metallicity models as being "in
redesign", and [M/H] = -2 was the highest metallicity for which all models
were listed as available:

    https://web.archive.org/web/20100723053826/http://www.hs.uni-hamburg.de/EN/For/ThA/phoenix/gaia_info.html

Older versions of the Gaia grid on the same server, such as the
``AMES-cond-giant`` v2.6 files from 2003 that are sampled every 2 Angstrom,
are a different computation and do not reproduce the files here.

## Solar PHOENIX (the ``'solar'`` set)

The PHOENIX tables of the ``'solar'`` set have [M/H] = 0 and cover 2000 to
4000 K in steps of 100 K. T. Richardson made them in January 2026 for the
R24 v1.3 models (commit ``b446dde`` on the ``new_atmos`` branch of
https://github.com/richardson-t/mysg, where they replaced the bundled
PHOENIX files under the same names). They are not included in mysg:
``solar_phoenix_table`` in ``mysg/atmosphere.py`` makes each table from its
source spectrum the first time it is needed, and checks that the result is
identical to the R24 v1.3 table.

The source spectra are the ``g40`` (log g = 4.0) column of the STScI CDBS
files

    https://archive.stsci.edu/hlsps/reference-atlases/cdbs/grid/phoenix/phoenixm00/phoenixm00_{temperature}.fits

whose headers give ``CREATED = '2021-5-10'``, ``MAPKEY = 'phoenixBTS11_15'``,
``DESCRIP = 'Phoenix Models BT-settl Allard et al. 03, 07, 09'`` and
``METAL10 = '-0.0'`` (the server gives a modification date of 2021-05-17 for
all 21 files). They are BT-Settl models (Allard et al. 2012) sampled at
103,000 wavelengths from 12.6 Angstrom to 77.6 micron. For the same
temperatures, the BT-Settl spectra with the Asplund et al. (2009) solar
abundances ("BT-Settl AGSS2009") on the SVO Theory service agree with them
closely (see the last section). The other metallicities of the STScI PHOENIX
grid are an older (2011) delivery that subsamples the spectra point by
point, which misrepresents the molecular bands of cool stars, so they are
not used.

Each table was made as follows:

* The flux per unit wavelength was converted to the flux per unit
  frequency, F_nu = F_lambda lambda^2 / c, and multiplied by pi^2 / 2 times
  the solid angle of 1 arcsec^2 in sr (1.16e-10). The tables are therefore
  proportional to the surface flux and are not normalized. The constant
  factor cancels when Hyperion scales the spectrum to the stellar luminosity.
* The columns are the wavelength (``wav``, in microns), the frequency
  (``nu``, in Hz) and ``fnu``, in order of increasing frequency.
* One point was added at a wavelength of 1 cm. Its value does not follow
  from the source spectrum by any recorded rule, so mysg stores the 21
  values (in ``phoenix_solar.json``). Relative to the last point of the
  source spectrum (77.6 micron), they correspond to F_nu proportional to
  lambda^-1.96 to lambda^-1.98, close to the Rayleigh-Jeans slope of -2.
  The part of the tables beyond 77.6 micron holds 6e-6 to 5e-5 of the
  luminosity.

The tables were made with ``astropy.units``. ``mysg/atmosphere.py`` uses the
values of the constants that astropy gives (for example
c = 2.9979245799999995e18 Angstrom/s) so that it reproduces the tables bit
for bit.

Because these tables are not normalized, the interpolation weights the two
closest tables by their surface flux, which scales as T^4: at 3050 K, the
3100 K table provides 53% of the luminosity (50% for normalized tables).

For each temperature, ``phoenix_solar.json`` records the SHA-256 of the
table values (as little-endian 64-bit floats, see ``table_sha256``), of the
STScI file as downloaded on 2026-11-19, and of the HDF5 file used for the
R24 v1.3 models. To use the set without network access, write it to a
directory with ``python scripts/make_atmospheres.py solar OUTDIR`` and pass
``atmospheres=OUTDIR``.

The Kurucz tables of the ``'solar'`` set are the bundled ones (below).

## Kurucz (the ``'r17'`` and ``'solar'`` sets)

The files in ``atmos/kurucz/`` are named
``kt{temperature:05d}g+4.0z-2.0.hdf5`` and cover 3500 to 39000 K (in steps of
250 K up to 13000 K and 1000 K above). They are the solar metallicity
([M/H] = 0) models of Castelli & Kurucz (2003).

The ``z-2.0`` in the names of these files is confusing, because it does not
mean [M/H] = -2 as it does for the PHOENIX files. It was carried over from
the names of older files, and the most it can be taken to mean is a metal
mass fraction of roughly 1%, which is approximately solar. These are solar
metallicity models.

The files match the ``g40`` (log g = 4.0) column of the ``ckp00`` models at

    https://archive.stsci.edu/hlsps/reference-atlases/cdbs/grid/ck04models/ckp00/

to within 0.05% at all 65 temperatures, once those are normalized in the same
way. The only other difference is an extra point at a wavelength of 1 cm.

## Sets with one metallicity at all temperatures

``python scripts/make_atmospheres.py MH OUTDIR`` writes a directory with the
same layout (``phoenix/`` and ``kurucz/``) in which both families have
[M/H] = MH, for use with ``setup_model(..., atmospheres=OUTDIR)``. All
spectra have log g = 4.0 and scaled-solar abundances, and the ``z`` in the
file names is the [M/H] of both families.

* Below 4000 K: BT-Settl AGSS2009 models (Allard et al. 2012), downloaded
  from the SVO Theory service (http://svo2.cab.inta-csic.es/theory/newov2/,
  model ``bt-settl-agss``, alpha = 0), resampled with flux conservation onto
  the wavelength grid of the STScI ``phoenixm00`` files, and converted in the
  same way as the solar PHOENIX tables (not normalized). The point at 1 cm
  continues the spectrum from 77.6 micron with F_nu proportional to
  lambda^-2. The STScI ``phoenixm00`` grid (delivered in 2021) is the
  [M/H] = 0 member of the same models. Scaled-solar spectra with log g = 4.0
  exist for 2000-4000 K at [M/H] = -0.5, 0.0, +0.3 and +0.5; at
  [M/H] = -1.0 the grid has only alpha-enhanced spectra, above 2600 K.
* At and above 4000 K: the Castelli & Kurucz (2003) models from the STScI
  ``ck04models`` grid (``ckm05``, ``ckp00``, ``ckp05``, ...), column ``g40``,
  converted as the bundled Kurucz files.

``scripts/atmospheres_sha256.json`` records the SHA-256 of every table and
downloaded spectrum of the sets with [M/H] = -0.5, 0 and +0.5 (spectra
downloaded on 2026-11-19), and of the ``'solar'`` set written by
``make_atmospheres.py solar``. The script compares each new build with these
values.

For MH = 0 the PHOENIX tables agree with the solar PHOENIX tables (made from
the STScI ``phoenixm00`` files) to 0.0006 in the fraction of the luminosity
in each broad band (0.4-0.7, 0.7-1, 1-2.5, 2.5-5 and 5-30 micron) at all
temperatures but 2600 K, where the SVO and STScI spectra differ by up to
0.0016 (up to 4% in 0.1 dex bands between 0.7 and 1.8 micron). The Kurucz
tables agree with the bundled ones to 0.05% (99th percentile; 2% at the 1 cm
point).

From 2300 to 4000 K the fraction of the luminosity in each band changes
monotonically with [M/H] from -0.5 to +0.5. At 2000-2200 K, where the
BT-Settl atmospheres have dust clouds, it does not, and the solar spectra at
2000 K and 2100 K differ more from each other (0.12 of the luminosity moves
between bands) than any other neighbouring pair.

## References

* Allard, F., Homeier, D. & Freytag, B. 2012, "Models of very-low-mass
  stars, brown dwarfs and exoplanets", Phil. Trans. R. Soc. A, 370, 2765
  (arXiv:1112.3591)
* Asplund, M., Grevesse, N., Sauval, A. J. & Scott, P. 2009, "The Chemical
  Composition of the Sun", ARA&A, 47, 481
* Brott, I. & Hauschildt, P. H. 2005, "A PHOENIX Model Atmosphere Grid for
  Gaia", in The Three-Dimensional Universe with Gaia, ed. C. Turon,
  K. S. O'Flaherty & M. A. C. Perryman, ESA SP-576, 565
  (arXiv:astro-ph/0503395)
* Castelli, F. & Kurucz, R. L. 2003, "New Grids of ATLAS9 Model Atmospheres",
  in IAU Symposium 210, Modelling of Stellar Atmospheres, ed. N. Piskunov et
  al., poster A20 (arXiv:astro-ph/0405087)
* Robitaille, T. P. 2017, "A new set of radiative transfer models for young
  stellar objects", A&A, 600, A11
