# Where did the data come from?

The ``atmos`` directory contains the stellar photosphere models used for the
central sources. PHOENIX models are used for T < 4000 K and Kurucz models for
T >= 4000 K, and the spectrum for a given temperature is found by linear
interpolation between the two closest models. All models have log g = 4.0.

Each file contains a table with the frequency (``nu``, in Hz) and the flux
per unit frequency (``fnu``), normalized so that the integral of the flux
over frequency is 1. The PHOENIX files also contain the wavelength (``wav``,
in microns).

Note that the two sets of models do not have the same metallicity: the
PHOENIX models have [M/H] = -2 (1/100 solar) and the Kurucz models have solar
metallicity, even though the file names of both contain ``z-2.0`` (see
below). The stellar spectra therefore change metallicity at 4000 K.

## PHOENIX

The files in ``atmos/phoenix/`` are named
``pt{temperature:05d}g+4.0z-2.0.hdf5`` and cover 2000 to 4000 K in steps of
100 K. They are PHOENIX models from the grid computed for the Gaia mission
(Brott & Hauschildt 2005), with [M/H] = -2.0 and no alpha enhancement. For
these files, the ``z-2.0`` in the name is the PHOENIX [M/H].

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

## Kurucz

The files in ``atmos/kurucz/`` are named
``kt{temperature:05d}g+4.0z-2.0.hdf5`` and cover 3500 to 39000 K (in steps of
250 K up to 13000 K and 1000 K above). They are the solar metallicity
([M/H] = 0) models of Castelli & Kurucz (2004).

The ``z-2.0`` in the names of these files is confusing, because it does not
mean [M/H] = -2 as it does for the PHOENIX files. It was carried over from
the names of older files, and the most it can be taken to mean is a metal
mass fraction of roughly 1%, which is approximately solar. These are solar
metallicity models.

The files match the ``g40`` (log g = 4.0) column of the ``ckp00`` models at

    https://archive.stsci.edu/hlsps/reference-atlases/cdbs/grid/ck04models/ckp00/

to within 0.05% at all 65 temperatures, once those are normalized in the same
way. The only other difference is an extra point at a wavelength of 1 cm.

## References

* Brott, I. & Hauschildt, P. H. 2005, "A PHOENIX Model Atmosphere Grid for
  Gaia", ESA SP-576, 565
* Castelli, F. & Kurucz, R. L. 2004, "New Grids of ATLAS9 Model Atmospheres",
  arXiv:astro-ph/0405087
