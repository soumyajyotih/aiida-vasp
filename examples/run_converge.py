import click
import os
from aiida.common.extendeddicts import AttributeDict
from aiida.cmdline.utils.decorators import with_dbenv

from aiida_vasp.utils.aiida_utils import get_data_node
from auxiliary import example_param_set, set_structure_si, set_kpoints, set_params_simple, set_params_simple_no_encut


@click.command()
@example_param_set
@with_dbenv()
def main(potential_family, queue, code, computer):
    from aiida.orm import Code
    from aiida.plugins import WorkflowFactory
    from aiida.engine import submit, run
    from aiida_vasp.utils.aiida_utils import get_data_class

    # fetch the code to be used (tied to a computer)
    code = Code.get_from_string('{}@{}'.format(code, computer))

    # set the WorkChain you would like to call
    workchain = WorkflowFactory('vasp.converge')

    # organize options (needs a bit of special care)
    options = AttributeDict()
    options.account = ''
    options.qos = ''
    options.resources = {'num_machines': 1, 'num_mpiprocs_per_machine': 20}
    options.queue_name = ''
    options.max_wallclock_seconds = 3600

    # organize settings
    settings = AttributeDict()
    # the workchains should configure the required parser settings on the fly
    parser_settings = {}
    settings.parser_settings = parser_settings

    # set inputs for the following WorkChain execution

    inputs = AttributeDict()
    # set code
    inputs.code = code
    # set structure
    inputs.structure = set_structure_si()
    # set k-points grid density (do not supply if you want to perform convergence tests on this)
    inputs.kpoints = set_kpoints(inputs.structure)
    # set parameters (do not supply plane wave cutoff if you want to perform convergence
    # tests on this)
    inputs.parameters = set_params_simple_no_encut()
    #inputs.parameters = set_params_simple()
    # set potentials and their mapping
    inputs.potential_family = get_data_class('str')(potential_family)
    inputs.potential_mapping = get_data_node('dict', dict={'Si': 'Si'})
    # set options
    inputs.options = get_data_node('dict', dict=options)
    # set settings
    inputs.settings = get_data_node('dict', dict=settings)
    # set workchain related inputs
    inputs.relax = get_data_node('bool', False)
    inputs.converge_relax = get_data_node('bool', False)
    inputs.encut_samples = get_data_node('int', 2)
    inputs.k_samples = get_data_node('int', 3)
    inputs.verbose = get_data_node('bool', True)
    inputs.compress = get_data_node('bool', False)
    inputs.displace = get_data_node('bool', False)
    # submit the requested workchain with the supplied inputs
    submit(workchain, **inputs)


if __name__ == '__main__':
    main()
