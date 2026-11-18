1.2 (unreleased)
----------------

- Fixed critical bug: the dust file included since version 1.0.1 contained
  optical properties computed with a version of bhmie that had a bug, which
  gave an incorrect albedo and scattering matrix. The dust file is no longer
  included and is instead generated from the hyperion-dust package, which is
  now a required dependency. The extinction in the new file is within 1% of
  that in the previous one (it is not identical because the minimum grain
  size and the abundances used are slightly different). Models computed with
  versions 1.0.1 and 1.1 used the incorrect optical properties.

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
