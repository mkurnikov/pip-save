from abc import abstractmethod
from collections import OrderedDict
from typing import Union

from distlib.markers import interpret
from distlib.version import LegacyMatcher

from pip_save.toml.model import Table
from pip_save.toml.parser import InlineTable


class UnsupportedVCSProtocolError(Exception):
    pass


class InvalidEnvironmentMarkers(SyntaxError):
    pass


DependencyTypes = Union['VersionedDependency', 'VCSDependency']


class VersionMatcher(LegacyMatcher):
    @property
    def specifiers(self):
        specs = []
        for operator, vers, _ in self._parts:
            specs.append(operator + str(vers))

        return ','.join(specs)


def parse_dependency(dep_name: str, dep_metadata: Union[Table, InlineTable, str]) -> DependencyTypes:
    if isinstance(dep_metadata, str) or \
            (isinstance(dep_metadata, InlineTable) and 'version' in dep_metadata):
        return VersionedDependency.parse_from_toml(dep_name, dep_metadata)


class Dependency(object):
    def __init__(self, pkg_name: str) -> None:
        self.pkg_name = pkg_name

    def __repr__(self):
        return str(self)

    @classmethod
    @abstractmethod
    def parse_from_toml(cls, dep_name: str, dep_metadata) -> 'Dependency':
        pass


class VersionedDependency(Dependency):
    def __init__(self, pkg_name: str, version_spec: str, markers=None) -> None:
        super().__init__(pkg_name)
        self.matcher = VersionMatcher('{pkg_name} ({spec})'
                                      .format(pkg_name=self.pkg_name,
                                              spec=version_spec))
        self.markers = markers

    # def __str__(self):
    #     arguments = '({name}, "{version_spec}")'.format(name=self.pkg_name,
    #                                                     version_spec=self.matcher.specifiers)
    #     return 'VersionedDependency' + arguments

    @classmethod
    def parse_from_toml(cls, dep_name: str, dep_metadata: Union[str, InlineTable]) -> 'VersionedDependency':
        if isinstance(dep_metadata, str):
            return VersionedDependency(dep_name, dep_metadata)

        version = dep_metadata['version']
        markers = None
        if 'markers' in dep_metadata:
            markers = dep_metadata['markers']
            try:
                interpret(markers)
            except SyntaxError as e:
                raise InvalidEnvironmentMarkers(e.args[0])

        return VersionedDependency(dep_name, version, markers=markers)


class VCSDependency(Dependency):
    def __init__(self, pkg_name, protocol, url, editable=False) -> None:
        super().__init__(pkg_name)
        if protocol not in ['git', 'svn', 'hg', 'bzr']:
            raise UnsupportedVCSProtocolError(protocol)

        self.protocol = protocol
        self.url = url
        self.editable = editable

    def for_toml(self):
        content = OrderedDict()
        content[self.protocol] = self.url
        content['editable'] = self.editable
        return InlineTable(content)
