# Where did the data come from?

## PHOENIX
The PHOENIX model grids were those prepared for the Gaia mission:
https://web.archive.org/web/20100405031408/http://www.hs.uni-hamburg.de/EN/For/ThA/phoenix/gaia_info.html

It is possible some of these files are still retrievable from the Hamburg FTP:
ftp://ftp.hs.uni-hamburg.de/pub/outgoing/phoenix/GAIA/
but the exact files, with the same name scheme, are not obviously available.

The files in this repository in the ``phoenix/`` directory are labeled as ``pt{temperature:05d}+4.0z-2.0.hdf5``, where the +4.0 indicates the gravity and z-2.0 indicates that these are 1/100 solar metallicity.  1/100 solar metallicity was used because solar metallicity atmospheres were not available at the time.

By default, PHOENIX models are used at T<4000 K.

## Kurucz
The Kurucz models are used above T >= 4000 K.  They are labeled ``kt{temperature:05d}+4.0z-2.0.hdf5``.  For these models, ``z-2.0`` indicates either Z=0.01, i.e., 1% metals = solar metallicity, or the label is simply incorrect.  These can be validated against the models here:
https://archive.stsci.edu/hlsps/reference-atlases/cdbs/grid/k93models/kp00/
