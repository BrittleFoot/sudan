import re

from os import popen, system
from logging import getLogger
from dataclasses import dataclass
from distutils.spawn import find_executable


log = getLogger('sudan.tools')
BIDEC = r'(\d+\.\d+)'


PARALLEL = 'parallel'
ARAGORN = 'aragorn'
RNAMMER = 'rnammer'
BARRNAP = 'barrnap'
PRODIGAL = 'prodigal'
SIGNALP = 'signalp'
MINCED = 'minced'
CMSCAN = 'cmscan'
CMPRESS = 'cmpress'
HMMSCAN = 'hmmscan'
HMMPRESS = 'hmmpress'
BLASTP = 'blastp'
MAKEBLASTDB = 'makeblastdb'
TBL2ASN = 'tbl2asn'


@dataclass
class _Tool:
    """ Tmp class to define initialization data """
    name: str
    getver: str
    regexp: str
    minver: str
    needed: bool

    @classmethod
    def standard_tool(cls, name):
        return cls(name, None, None, None, needed=True)


@dataclass
class Tool:
    name: str
    version: str
    have: bool


class Toolkit:

    def __lazy_init_tool(self, name) -> Tool:
        utn = '__' + name
        if hasattr(self, utn):
            return getattr(self, utn)
        ver, have = _check_tool(getattr(_Toolkit, name))
        setattr(self, utn, Tool(name, ver, have))
        return getattr(self, utn)

    @property
    def parallel(self) -> Tool:
        return self.__lazy_init_tool(PARALLEL)

    @property
    def aragorn(self) -> Tool:
        return self.__lazy_init_tool(ARAGORN)

    @property
    def rnammer(self) -> Tool:
        return self.__lazy_init_tool(RNAMMER)

    @property
    def barrnap(self) -> Tool:
        return self.__lazy_init_tool(BARRNAP)

    @property
    def cmscan(self) -> Tool:
        return self.__lazy_init_tool(CMSCAN)

    @property
    def minced(self) -> Tool:
        return self.__lazy_init_tool(MINCED)

    @property
    def prodigal(self) -> Tool:
        return self.__lazy_init_tool(PRODIGAL)

    def init_all(self):
        for name in Toolkit.__dict__:
            if name.startswith('_') or name != 'init_all':
                continue
            # warm'em up
            getattr(self, name)


class _Toolkit:
    # just the standard unix tools we need
    # yes, we need this before we can test versions :-/
    grep = _Tool.standard_tool('grep')
    egrep = _Tool.standard_tool('egrep')
    sed = _Tool.standard_tool('sed')
    find = _Tool.standard_tool('find')
    java = _Tool.standard_tool('java')
    # for the new --proteins option ability to take .gbk or .embl files
    genbank = _Tool.standard_tool('prokka-genbank_to_fasta_db')

    parallel = _Tool(
        PARALLEL,
        "parallel --version | grep -E 'parallel 2[0-9]{7}$'",
        re.compile(r'parallel (\d+)'),
        "20130422",
        True
    )
    aragorn = _Tool(
        ARAGORN,
        "aragorn -h 2>&1 | grep -i '^ARAGORN v'",
        re.compile(rf'{BIDEC}'),
        "1.2",
        True
    )
    rnammer = _Tool(
        RNAMMER,
        "rnammer -V 2>&1 | grep -i 'rnammer [0-9]'",
        re.compile(rf'{BIDEC}'),
        "1.2",
        False
    )
    barrnap = _Tool(
        BARRNAP,
        "LC_ALL=C barrnap --version 2>&1",
        re.compile(rf'{BIDEC}'),
        "0.4",
        False
    )
    prodigal = _Tool(
        PRODIGAL,
        "prodigal -v 2>&1 | grep -i '^Prodigal V'",
        re.compile(rf'{BIDEC}'),
        "2.6",
        True
    )
    signalp = _Tool(
        SIGNALP,
        # this is so long-winded as -v changed meaning 
        # (3.0=version, 4.0=verbose !?)
        "if [ \"`signalp -version 2>&1 | "
        "grep -Eo '[0-9]+\\.[0-9]+'`\" != \"\" ]; "
        "then echo `signalp -version 2>&1 | "
        "grep -Eo '[0-9]+\\.[0-9]+'`; "
        "else signalp -v < /dev/null 2>&1 | egrep ',|# SignalP' | "
        "sed 's/^# SignalP-//'; fi",
        re.compile(rf'^{BIDEC}'),
        "3.0",
        False
    )
    minced = _Tool(
        MINCED,
        "minced --version | sed -n '1p'",
        re.compile(rf'minced\s+\d+\.{BIDEC}'),
        "2.0",
        False  # really 0.3 as we skip first number.
    )
    cmscan = _Tool(
        CMSCAN,
        "cmscan -h | grep '^# INFERNAL'",
        re.compile(rf'INFERNAL\s+{BIDEC}'),
        "1.1",
        False
    )
    cmpress = _Tool(
        CMPRESS,
        "cmpress -h | grep '^# INFERNAL'",
        re.compile(rf'INFERNAL\s+{BIDEC}'),
        "1.1",
        False
    )
    hmmscan = _Tool(
        HMMSCAN,
        "hmmscan -h | grep '^# HMMER'",
        re.compile(rf'HMMER\s+{BIDEC}'),
        "3.1",
        True
    )
    hmmpress = _Tool(
        HMMPRESS,
        "hmmpress -h | grep '^# HMMER'",
        re.compile(rf'HMMER\s+{BIDEC}'),
        "3.1",
        True
    )
    blastp = _Tool(
        BLASTP,
        "blastp -version",
        re.compile(rf'blastp:\s+{BIDEC}'),
        "2.8",
        True
    )
    makeblastdb = _Tool(
        MAKEBLASTDB,
        "makeblastdb -version",
        re.compile(rf'makeblastdb:\s+{BIDEC}'),
        "2.8",
        False
    )
    tbl2asn = _Tool(
        TBL2ASN,
        "tbl2asn - | grep '^tbl2asn'",
        re.compile(rf'tbl2asn\s+{BIDEC}'),
        "24.3",
        True
    )


def _parse_version(s_version):
    return tuple(map(int, s_version.split('.')))


def _check_tool(tool):
    executable = find_executable(tool.name)
    if not executable and tool.needed:
        raise Exception(
            f'Required executable {tool.name} was not found in PATH')
    if not executable:
        log.debug(f'Tool {tool.name} not found. skipped.')
        return False, '0'
    if not tool.getver:
        return True, '1'

    ver_output = popen(tool.getver).read().strip()

    match = tool.regexp.search(ver_output)
    if not match:
        raise Exception(f'Cound not determine version of {tool.name}. ' +
                        f'Please install version {tool.minver} or higher')

    s_version = match.group(1)
    version = _parse_version(s_version)
    min_version = _parse_version(tool.minver)

    if version < min_version:
        raise Exception(
            f'Tool {tool.name} version required {min_version} or higher')

    log.debug(f'Found {tool.name}:{s_version}')

    return True, s_version


class ToolRunException(Exception):
    def __init__(self, code, cmd):
        super().__init__(f'[{code}] {cmd}')


def run_tool(cmd, nofail=False):
    log.info('$ ' + cmd)
    err = system(cmd)
    if nofail == True:
        return err

    if err != 0:
        raise ToolRunException(err, cmd)

    return err
