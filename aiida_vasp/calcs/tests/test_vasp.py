# pylint: disable=unused-import,unused-argument,redefined-outer-name
"""Unittests for VaspCalculation"""
import contextlib

import pytest

from aiida_vasp.utils.fixtures import aiida_env, fresh_aiida_env, localhost, vasp_params, paws, cif_structure, kpoints_mesh, vasp_code


@pytest.fixture()
def vasp_calc_s1(vasp_code, vasp_params, paws):
    """Fixture for non varying setup of a vasp calculation"""
    from aiida_vasp.calcs.vasp import VaspCalculation
    calc = VaspCalculation()
    calc.use_code(vasp_code)
    calc.set_computer(vasp_code.get_computer())
    calc.set_resources({'num_machines': 1, 'num_mpiprocs_per_machine': 1})
    calc.use_parameters(vasp_params)
    calc.use_paw(paws['In'], kind='In')
    calc.use_paw(paws['As'], kind='As')
    return calc


@pytest.fixture()
def vasp_calc_cif(vasp_calc_s1, cif_structure, kpoints_mesh):
    """Fixture for a vasp calculation with a cif structure input"""
    vasp_calc_s1.use_structure(cif_structure)
    vasp_calc_s1.use_kpoints(kpoints_mesh)
    return vasp_calc_s1


def test_store(vasp_calc_cif):
    vasp_calc_cif.store_all()
    assert vasp_calc_cif.pk is not None


def test_write_incar(vasp_calc_cif):
    from aiida_vasp.backendtests.common import subpath
    inp = vasp_calc_cif.get_inputs_dict()
    with managed_temp_file() as temp_file:
        vasp_calc_cif.write_incar(inp, temp_file)
        with open(temp_file, 'r') as result_incar_fo:
            with open(subpath('data/INCAR'), 'r') as reference_incar_fo:
                assert result_incar_fo.read() == reference_incar_fo.read()


@contextlib.contextmanager
def managed_temp_file():
    import os
    import tempfile
    _, temp_file = tempfile.mkstemp()
    try:
        yield temp_file
    finally:
        os.remove(temp_file)
