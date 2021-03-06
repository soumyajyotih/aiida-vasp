"""Test the DOSCAR parser."""
# pylint: disable=unused-import,redefined-outer-name,unused-argument,unused-wildcard-import,wildcard-import

import pytest
import numpy

from aiida_vasp.utils.fixtures import *
from aiida_vasp.utils.fixtures.testdata import data_path
from aiida_vasp.parsers.file_parsers.doscar import DosParser


def test_parse_doscar(fresh_aiida_env):
    """Parse a reference DOSCAR file with the DosParser and compare the result to a reference."""
    file_name = 'DOSCAR'
    path = data_path('doscar', file_name)
    parser = DosParser(file_path=path)
    dos = numpy.array([(-3.44, -1.10400000e-43, -2.09900000e-43),
                       (-1.539, 1.40000000e-01, 2.66100000e-01),
                       (0.362, -3.62400000e-73, 2.00000000e+00),
                       (2.264, -1.33800000e-05, 2.00000000e+00),
                       (4.165, 3.15600000e+00, 8.00000000e+00),
                       (6.066, -2.41200000e-15, 8.00000000e+00),
                       (7.967, 3.15600000e+00, 1.40000000e+01),
                       (9.868, -1.38100000e-27, 1.40000000e+01),
                       (11.769, 2.90100000e+00, 1.95200000e+01),
                       (13.67, 0.00000000e+00, 2.00000000e+01)],
                      dtype=[('energy', '<f8'), ('total', '<f8'), ('integrated', '<f8')])  # yapf: disable
    result = parser.dos
    # The 'tdos' array is a nested array for some reason.
    result_dos = result.get_array('tdos')
    for i in range(0, dos.size):
        assert result_dos[i] == dos[i]

    file_name = 'DOSCAR.nopdos'
    path = data_path('doscar', file_name)
    parser = DosParser(file_path=path)
    result = parser.dos
    # The 'tdos' array is a nested array for some reason.
    result_dos = result.get_array('tdos')
    assert 'pdos' not in result.get_arraynames()
    for i in range(0, dos.size):
        assert result_dos[i] == dos[i]


def test_parse_doscar_spin(fresh_aiida_env):
    """Parse a reference DOSCAR file with the DosParser and compare the result to a reference."""
    file_name = 'DOSCAR.spin'
    path = data_path('doscar', file_name)
    parser = DosParser(file_path=path)
    result = parser.dos

    result_dos = result.get_array('tdos')
    assert len(result_dos.dtype) == 3
    assert result_dos['total'].shape == (301, 2)

    result_dos = result.get_array('pdos')
    assert len(result_dos.dtype) == 10
    assert result_dos[0]['px'].shape == (301, 2)


def test_parse_doscar_ncl(fresh_aiida_env):
    """parse a reference doscar file with the dosparser and compare the result to a reference."""
    file_name = 'DOSCAR.ncl'
    path = data_path('doscar', file_name)
    parser = DosParser(file_path=path)
    result = parser.dos

    # tdos only has a single spin component
    result_dos = result.get_array('tdos')
    assert len(result_dos.dtype) == 3
    assert result_dos['total'].shape == (301,)

    result_dos = result.get_array('pdos')
    assert len(result_dos.dtype) == 10
    assert result_dos[0]['px'].shape == (301, 4)
