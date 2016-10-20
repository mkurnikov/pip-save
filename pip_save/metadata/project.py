import os
from contextlib import contextmanager
from typing import List

from pip_save.metadata.dependencies import Dependency, VersionedDependency
from pip_save.toml.assemble import parse_toml
from pip_save.toml.model import Root
from pip_save.toml.model import Table
from pip_save.toml.source import InvalidTomlError
from pip_save.toml.writer import to_toml


class Project(object):
    def __init__(self, root=None):
        self._root = root or Root()

        if 'deps' not in self._root:
            self._root['deps'] = Table()
        self._deps_table = self._root['deps']
        self.deps = []  # type: List[Dependency]
        for dep_name, dep_metadata in self._root['deps'].items():
            print(dep_name, dep_metadata)

        self.dev_deps = []  # type: List[Dependency]
        if 'dev_deps' not in self._root:
            self._root['dev_deps'] = Table()
        self._dev_deps_table = self._root['dev_deps']

    def add_dependency(self, dep: Dependency) -> None:
        self.deps.append(dep)
        if isinstance(dep, VersionedDependency):
            self._deps_table[dep.pkg_name] = dep.matcher.specifiers

    @classmethod
    def from_toml(cls, text: str) -> 'Project':
        root = parse_toml(text)
        return cls(root=root)

    def to_toml(self):
        return to_toml(self._root)



@contextmanager
def build_project_state(fpath):
    if not os.path.exists(fpath):
        raise InvalidTomlError('File {fpath} does not exist. Please, run "{init}" or create it manually.'
                              .format(fpath=fpath,
                                      init="packager init"))

    with open(fpath, 'r') as f:
        text = f.read()

    project = Project.from_toml(text)

    yield project
    out = project.to_toml()

    with open(fpath, 'w') as f:
        f.write(out)
