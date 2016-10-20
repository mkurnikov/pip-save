from abc import abstractmethod, ABCMeta
from collections import OrderedDict, namedtuple
from enum import Enum
from typing import Any
from typing import Dict
from typing import Tuple

from pip_save.toml.parser import ValueType, _parse_table_name
from pip_save.toml.source import Source


class NotSupported(Exception):
    pass


class UnboundedNodeException(Exception):
    pass


class ChangeEventType(Enum):
    Add = 1
    Remove = 2
    SetValue = 3


ChangeEvent = namedtuple('ChangeEvent', [
    'type',
    'node_name',
    'value'
])


class Node(metaclass=ABCMeta):
    def __init__(self, parent=None, parent_table_ref_key=None):
        self.parent = parent  # type: Node
        self.parent_table_ref_key = parent_table_ref_key  # type: str
        # self.parent = parent  # type: Optional[Node]
        # self.parent_table_ref_key = parent_table_ref_key

    @abstractmethod
    def process_change_event(self, event: ChangeEvent):
        raise NotImplementedError()


class Table(Node):
    def __init__(self, nodes=None, parent=None, parent_table_ref_key=None):
        super().__init__(parent, parent_table_ref_key)
        self.nodes = nodes or {}

    def process_change_event(self, event: ChangeEvent):
        if self.parent is None or self.parent_table_ref_key is None:
            raise ValueError('Every table has to have parent and parent_table_ref_key specified, '
                             'in order to process ChangeEvent objects.')

        processed_event = ChangeEvent(event.type, (self.parent_table_ref_key,) + event.node_name, event.value)
        self.parent.process_change_event(processed_event)

    def __setitem__(self, key, value):
        # check whether table exists in the AST (and not just added in process of table.nested.subnested creation)
        if isinstance(value, Table):
            raise NotImplementedError('Table could only be added from the top-level Root instance.')

        if key not in self.nodes:
            event_type = ChangeEventType.Add
        else:
            event_type = ChangeEventType.SetValue

        node_name = (key,)
        event = ChangeEvent(event_type, node_name, value)

        self.nodes[key] = value
        self.process_change_event(event)
        # if self.parent is None:
        #     raise UnboundTable()

    def __delitem__(self, key):
        event_type = ChangeEventType.Remove
        node_name = (key,)
        event = ChangeEvent(event_type, node_name, None)

        del self.nodes[key]
        self.process_change_event(event)

    def __getitem__(self, item):
        return self.nodes[item]

    def __contains__(self, item):
        return item in self.nodes

    def __eq__(self, other):
        return self.nodes == other.nodes

    def __str__(self):
        return 'Table({dict})'.format(dict=str(self.nodes))

    def __repr__(self):
        return str(self)

    def items(self):
        return self.nodes.items()


NodeName = Tuple[str, ...]


class TomlStatementNodes(object):
    def __init__(self, nodes_dict=None):
        self._statements = nodes_dict or OrderedDict()  # type: Dict[NodeName, Any]

    def add_root_keyword(self, key: str, value) -> None:
        first_table_name = None
        for node_name, val in self._statements.items():
            if isinstance(val, Table):
                first_table_name = node_name

        if first_table_name is None:
            self._statements[(key,)] = value
            return

        self.insert_before(first_table_name, (key,), value)

    def add_table_keyword(self, table_name: NodeName, key: str, value) -> None:
        if table_name not in self._statements:
            raise KeyError('No such table {}.'.format(table_name))

        previous_node_name = None
        inside_the_table = False
        for node_name, val in self._statements.items():
            # implement slices over OrderedDict?
            if isinstance(val, Table):
                if node_name == table_name:
                    inside_the_table = True
                else:
                    if inside_the_table:
                        break

            if inside_the_table:
                previous_node_name = node_name

        self.insert_after(previous_node_name, table_name + (key,), value)

    def insert_after(self, node_name: NodeName, new_node_name: NodeName, new_value) -> None:
        new_statements = OrderedDict()  # type: Dict[NodeName, Any]
        for key, val in self._statements.items():
            new_statements[key] = val
            if key == node_name:
                new_statements[new_node_name] = new_value

        self._statements = new_statements

    def insert_before(self, node_name: NodeName, new_node_name: NodeName, new_value) -> None:
        new_statements = OrderedDict()  # type: Dict[NodeName, Any]
        for key, val in self._statements.items():
            if key == node_name:
                new_statements[new_node_name] = new_value

            new_statements[key] = val
        self._statements = new_statements

        self._statements = new_statements

    def __setitem__(self, key: NodeName, value):
        self._statements[key] = value

    def __getitem__(self, item):
        return self._statements[item]

    def __delitem__(self, key):
        del self._statements[key]

    def __contains__(self, item: NodeName) -> bool:
        return item in self._statements

    def __len__(self) -> int:
        return len(list(self._statements.keys()))

    def keys(self):
        return list(self._statements.keys())

    def items(self):
        return list(self._statements.items())

    def __str__(self):
        return str(list(self._statements.items()))

    def __repr__(self):
        return str(self)


class Root(Table):
    def __init__(self, nodes=None, statement_nodes=None):
        super().__init__(nodes)
        self.statement_nodes = statement_nodes or TomlStatementNodes()

    def process_change_event(self, event: ChangeEvent) -> None:
        if event.value is None:
            # removals
            if len(event.node_name) == 1:
                del self.statement_nodes[event.node_name]
                return

        if isinstance(event.value, ValueType.__union_params__):
            if event.type == ChangeEventType.SetValue:
                self.statement_nodes[event.node_name] = event.value
                return

            elif event.type == ChangeEventType.Add:
                if len(event.node_name) == 1:
                    self.statement_nodes.add_root_keyword(event.node_name[-1], event.value)
                    return

                else:
                    # self.statement_nodes.insert_after()
                    self.statement_nodes.add_table_keyword(event.node_name[:-1], event.node_name[-1],
                                                           event.value)
                    return

            else:
                raise ValueError('ChangeEventType is Remove or not specified.')

        if isinstance(event.value, Table):
            if event.type == ChangeEventType.Add:
                self.statement_nodes[event.node_name] = Table()
                return

    def __setitem__(self, key, value):
        if not isinstance(value, Table):
            super().__setitem__(key, value)
            return

        s = Source(key)
        node_name = _parse_table_name(s)
        if len(s._text) > 0:
            raise ValueError('Invalid table name {}'.format(key))

        if node_name in self.statement_nodes:
            raise NotSupported('Table override is not supported.')

        current_table = self
        for part in node_name[:-1]:
            if part not in current_table:
                # can't use Table[item] = Table(), use .nodes
                current_table.nodes[part] = Table(parent=current_table,
                                                  parent_table_ref_key=part)

            current_table = current_table[part]

        current_table.nodes[node_name[-1]] = value
        value.parent = current_table
        value.parent_table_ref_key = node_name[-1]

        self.statement_nodes[node_name] = Table()

    def set_statement_nodes(self, nodes: TomlStatementNodes) -> None:
        self.statement_nodes = nodes

    def __str__(self):
        return 'Root({dict})'.format(dict=str(self.nodes))

    def __repr__(self):
        return str(self)
