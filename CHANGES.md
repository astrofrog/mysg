1.3 (unreleased)
----------------

- The default stellar atmospheres now have solar metallicity at all
  temperatures. Below 4000 K, they are the solar-metallicity PHOENIX
  (BT-Settl) spectra used for version 1.3 of the R24 models (T. Richardson),
  which are made from spectra downloaded from the STScI archive the first time
  they are needed and are checked against the recorded checksums. Previously,
  the atmospheres below 4000 K had [M/H] = -2. The Kurucz atmospheres, used at
  4000 K and above, are unchanged. Use ``atmospheres='r17'`` to reproduce
  models computed with earlier versions.

- Added the ``atmospheres`` option to ``setup_model`` and ``interp_atmos`` to
  select a set of stellar atmospheres: ``'solar'`` (the default), ``'r17'``
  (the bundled set) or a directory of tables.

- Added ``scripts/make_atmospheres.py`` to write the ``'solar'`` set to a
  directory (for computers without network access) and to make sets with one
  metallicity at all temperatures. The sources, conversion steps and checksums
  of all sets are described in ``mysg/data/README.md``.

1.2 (unreleased)
----------------

- Fixed critical bug: the dust file included since version 1.0.1 contained
  optical properties computed with a version of bhmie that had a bug, which
  gave an incorrect albedo and scattering matrix. The dust file is no longer
  included and is instead generated from the hyperion-dust package, which is
  now a required dependency. The extinction in the new file is within 1% of
  that in the previous one (it is not identical because the minimum grain
  size and the abundances used are slightly different). Models computed with
  versions 1.0.1, 1.1 and 1.1.1 used the incorrect optical properties.

1.1.1 (2026-11-19)
------------------

- Updated the package to work with Python 3.11 and later, and with current
  versions of Numpy, Astropy and Hyperion. Python 2 is no longer supported.

- The random seed used when sampling the parameters for a model set is now
  the same with Python 3 as it was with Python 2, so that sampling a model
  set gives the same model names and parameters as in the published sets.

- The package is now built with hatchling.

1.1 (2016-06-18)
----------------

- Added an option to disable image output, since we now compute the temperature
  and images in two steps.

1.0.1 (2015-02-23)
------------------

- Updated dust file to version 2 format

- Fixed critical bug: make sure that the cavity density never exceed envelope
  densities.

- Fixed critical bug: densities were not being subtracted from ambient density.

1.0.0
-----

- Initial version
