1.2 (unreleased)
----------------

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
