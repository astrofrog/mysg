import glob
import os

import h5py
import pytest

from mysg.hyperion_helper import setup_model
from mysg.models import export_dust_files, make_set_dir, sample_set_models
from mysg.parameters import read_parfile, write_parfile

N_MODELS = 3


# The first set is a 1-d model with a power-law envelope, and the second is a
# 2-d model that includes all the components that are implemented.
@pytest.mark.parametrize('set_name', ['s-p-hmi-', 'spubhmi-'])
def test_model_set(tmp_path, monkeypatch, set_name):

    directory = str(tmp_path)

    make_set_dir(directory, set_name)
    sample_set_models(directory, set_name, lambda n_free: N_MODELS)
    export_dust_files(directory)

    parfiles = sorted(glob.glob(os.path.join(directory, set_name, 'par', '*', '*.par')))
    assert len(parfiles) == N_MODELS

    # Sampling the same set again should give the same parameters
    os.mkdir(os.path.join(directory, 'repeat'))
    make_set_dir(os.path.join(directory, 'repeat'), set_name)
    sample_set_models(os.path.join(directory, 'repeat'), set_name, lambda n_free: N_MODELS)
    repeat = sorted(glob.glob(os.path.join(directory, 'repeat', set_name, 'par', '*', '*.par')))
    assert [os.path.basename(p) for p in repeat] == [os.path.basename(p) for p in parfiles]
    assert read_parfile(repeat[0]) == read_parfile(parfiles[0])

    # The dust files are referred to by name in the parameter files, so the
    # model has to be set up from the directory that contains them.
    monkeypatch.chdir(directory)

    setup_model(parfiles[0], 'model')

    with h5py.File('model.rtin', 'r') as f:
        assert 'Grid' in f
        assert 'Sources' in f


def test_optically_thick_envelope(tmp_path, monkeypatch, caplog):

    # For 1-d models, the inner envelope is removed if it is optically thick
    # at 5mm, which does not happen for the parameter ranges of the sets.

    export_dust_files(str(tmp_path))
    monkeypatch.chdir(tmp_path)

    write_parfile('thick.par', {'star.radius': 10.,
                                'star.temperature': 4000.,
                                'envelope.rho_0': 1.e-12,
                                'envelope.power': -2.,
                                'ambient.density': 1.e-23,
                                'ambient.temperature': 10.,
                                'envelope.dust': 'd03_5.5_3.0_A_sub.hdf5',
                                'ambient.dust': 'd03_5.5_3.0_A_sub.hdf5'})

    setup_model('thick.par', 'thick', imaging=False)

    assert 'truncating inner envelope' in caplog.text
    assert os.path.exists('thick.rtin')
