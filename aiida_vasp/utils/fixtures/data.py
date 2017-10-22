"""pytest-style test fixtures"""
# pylint: disable=unused-import,unused-argument,redefined-outer-name
import shutil

import numpy
import pytest

from aiida_vasp.utils.fixtures.environment import aiida_env, fresh_aiida_env


@pytest.fixture(scope='session')
def localhost_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('localhost_work')


@pytest.fixture()
def localhost(aiida_env, localhost_dir):
    """Fixture for a local computer called localhost"""
    from aiida.orm import Computer
    from aiida.orm.querybuilder import QueryBuilder
    query_builder = QueryBuilder()
    query_builder.append(Computer, tag='comp')
    query_builder.add_filter('comp', {'name': {'==': 'localhost'}})
    query_results = query_builder.all()
    if query_results:
        computer = query_results[0][0]
    else:
        computer = Computer(
            name='localhost',
            description='description',
            hostname='localhost',
            workdir=localhost_dir.strpath,
            transport_type='local',
            scheduler_type='direct',
            enabled_state=True)
    return computer


@pytest.fixture()
def vasp_params(aiida_env):
    from aiida.orm import DataFactory

    return DataFactory('parameter')(dict={
        'gga': 'PE',
        'gga_compat': False,
        'lorbit': 11,
        'sigma': 0.5
    })


@pytest.fixture()
def paws(aiida_env):
    """Fixture for two incomplete POTPAW potentials"""
    from aiida.orm import DataFactory
    from aiida_vasp.backendtests.common import subpath
    DataFactory('vasp.paw').import_family(
        subpath('../backendtests/LDA'),
        familyname='TEST',
        family_desc='test data',
    )
    paw_nodes = {
        'In': DataFactory('vasp.paw').load_paw(element='In')[0],
        'As': DataFactory('vasp.paw').load_paw(element='As')[0]
    }
    return paw_nodes


@pytest.fixture(params=['cif', 'str'])
def vasp_structure(request, aiida_env):
    """Fixture: StructureData or CifData"""
    from aiida_vasp.backendtests.common import subpath
    from aiida.orm import DataFactory
    if request.param == 'cif':
        cif_path = subpath('data/EntryWithCollCode43360.cif')
        structure = DataFactory('cif').get_or_create(cif_path)[0]
    elif request.param == 'str':
        larray = numpy.array([[0, .5, .5], [.5, 0, .5], [.5, .5, 0]])
        alat = 6.058
        structure = DataFactory('structure')(cell=larray * alat)
        structure.append_atom(position=[0, 0, 0], symbols='In')
        structure.append_atom(position=[.25, .25, .25], symbols='As')
    return structure


@pytest.fixture(params=['mesh', 'list'])
def vasp_kpoints(request, aiida_env):
    """Fixture: (kpoints object, resulting KPOINTS)"""
    from aiida.orm import DataFactory
    if request.param == 'mesh':
        kpoints = DataFactory('array.kpoints')()
        kpoints.set_kpoints_mesh([2, 2, 2])
        ref_kpoints = _ref_kp_mesh()
    elif request.param == 'list':
        kpoints = DataFactory('array.kpoints')()
        kpoints.set_kpoints([[0., 0., 0.], [0., 0., .5]], weights=[1., 1.])
        ref_kpoints = _ref_kp_list()
    return kpoints, ref_kpoints


@pytest.fixture()
def vasp_code(localhost):
    """Fixture for a vasp code, the executable it points to does not exist"""
    from aiida.orm import Code
    localhost.store()
    code = Code()
    code.label = 'vasp'
    code.description = 'VASP code'
    code.set_remote_computer_exec((localhost, '/usr/local/bin/vasp'))
    code.set_input_plugin_name('vasp.vasp')
    return code


@pytest.fixture()
def ref_incar():
    from aiida_vasp.backendtests.common import subpath
    with open(subpath('data/INCAR'), 'r') as reference_incar_fo:
        yield reference_incar_fo.read()


def _ref_kp_list():
    from aiida_vasp.backendtests.common import subpath
    with open(subpath('data/KPOINTS.list'), 'r') as reference_kpoints_fo:
        ref_kp_str = reference_kpoints_fo.read()
    return ref_kp_str


def _ref_kp_mesh():
    from aiida_vasp.backendtests.common import subpath
    with open(subpath('data/KPOINTS.mesh'), 'r') as reference_kpoints_fo:
        ref_kp_list = reference_kpoints_fo.read()
    return ref_kp_list
