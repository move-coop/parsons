import collections
import copy


SQLStatement = collections.namedtuple('SQLStatement', ['sql', 'params'])
JoinInfo = collections.namedtuple('JoinInfo',
                                  ['join_type', 'join_table', 'join_condition'])
FromInfo = collections.namedtuple('FromInfo', ['relation', 'alias', 'parameters'])
OrderByInfo = collections.namedtuple('OrderByInfo', ['expression', 'direction'])
WhereInfo = collections.namedtuple('WhereInfo', ['expression', 'parameters', 'conjunction'])


class SelectStatementBuilder:
    """Class for building SQL statements programmatically.

    By calling the methods on the class, users can construct a SQL query in Python. To generate
    the SQL statement, use the `build` method.

    The builder class is immutable, which means each call to the class creates a new instance
    and returns the new instance. The original is not modified.

    .. code-block:: python

    statement = (SelectStatementBuilder()
                 .select('one', 'two')
                 .from_('table')
                 .where('one = %', [1])
                 .build())
    rs.query(statement.sql, statement.parameters)

    """
    def __init__(self):
        self.select_columns = []
        self.from_infos = []
        self.where_infos = []
        self.join_infos = []
        self.group_by_expressions = []
        self.limit_number = None
        self.offset_start = None
        self.order_by_infos = []

    def select(self, *columns):
        """Specify which columns to select."""
        clone = self._clone()
        clone.select_columns = columns
        return clone

    def from_(self, relation, alias=None):
        """Specify the relation or subquery to select data from."""
        clone = self._clone()
        parameters = []
        if hasattr(relation, 'build'):
            statement = relation.build()
            relation = f'({statement.sql})'
            parameters = statement.params
        clone.from_infos.append(FromInfo(relation, alias, parameters))
        return clone

    def join(self, join_table, join_condition):
        """Join another table into the query using an inner join.

        """
        return self._join(None, join_table, join_condition)

    def left_join(self, join_table, join_condition):
        """Join another table into the query using a left outer join.

        """
        return self._join('left', join_table, join_condition)

    def right_join(self, join_table, join_condition):
        """Join another table into the query using a right outer join.

        """
        return self._join('right', join_table, join_condition)

    def full_join(self, join_table, join_condition):
        """Join another table into the query using a full outer join.

        """
        return self._join('full', join_table, join_condition)

    def where(self, condition, parameters=None):
        """Filter the query down based on a condition.

        Additional calls will append another clause to the query using 'and's.

        """
        return self._where(condition, parameters, 'and')

    def and_(self, condition, parameters=None):
        """Further filter the query down based on a condition.

        """
        return self._where(condition, parameters, 'and')

    def or_(self, condition, parameters=None):
        """Further filter the query down based on a condition.

        """
        return self._where(condition, parameters, 'or')

    def group_by(self, expression):
        """Group the results of your query by an expression.

        Additional calls will append another expression to the group by.

        """
        clone = self._clone()
        clone.group_by_expressions.append(expression)
        return clone

    def having(self, condition):
        raise NotImplementedError('This method is not yet implemented')

    def union(self, query):
        raise NotImplementedError('This method is not yet implemented')

    def intersect(self, query):
        raise NotImplementedError('This method is not yet implemented')

    def except_(self, query):
        raise NotImplementedError('This method is not yet implemented')

    def minus(self, query):
        raise NotImplementedError('This method is not yet implemented')

    def order_by(self, expression, asc_desc=None):
        """Order the results of your query by an expression.

        Additional calls will append another expression to the order by.

        """
        clone = self._clone()
        clone.order_by_infos.append(OrderByInfo(expression, asc_desc))
        return clone

    def limit(self, number):
        """Limit the number of records to return in your query.

        """
        clone = self._clone()
        clone.limit_number = number
        return clone

    def offset(self, start):
        """Specify an offset for the results of your query.

        """
        clone = self._clone()
        clone.offset_start = start
        return clone

    def build(self):
        """Generate a SQL statement based on the current state of the builder.

        """
        select_columns = ', '.join(self.select_columns)
        select_clause = f'select {select_columns}'
        all_parameters = []

        from_clauses = [
            f' from {info.relation}{f" as {info.alias}" if info.alias else ""}'
            for info in self.from_infos
        ]
        from_clause = ', '.join(from_clauses)
        for info in self.from_infos:
            all_parameters = all_parameters + info.parameters

        join_clause = ''
        if self.join_infos:
            pass

        where_clause = ''
        if self.where_infos:
            where_expressions = []
            for index, info in enumerate(self.where_infos):
                expr = f'{info.conjunction} ' if index > 0 else ''
                expr += info.expression
                where_expressions.append(expr)
            where_all = ' '.join(where_expressions)
            where_clause = f' where {where_all}'
            for info in self.where_infos:
                all_parameters = all_parameters + info.parameters

        group_by_clause = ''
        if self.group_by_expressions:
            group_bys = ', '.join(self.group_by_expressions)
            group_by_clause = f' group by {group_bys}'

        order_by_clause = ''
        if self.order_by_infos:
            order_by_expressions = [
                f'{info.expression}{f" {info.direction}" if info.direction else ""}'
                for info in self.order_by_infos
            ]
            order_bys = ', '.join(order_by_expressions)
            order_by_clause = f' order by {order_bys}'

        limit_clause = ''
        if self.limit_number:
            limit_clause = f' limit {self.limit_number}'

        offset_clause = ''
        if self.offset_start:
            offset_clause = f' offset {self.offset_start}'

        query = (
            f'{select_clause}{from_clause}{join_clause}{where_clause}'
            f'{group_by_clause}{order_by_clause}{limit_clause}{offset_clause}'
        )

        return SQLStatement(query, all_parameters)

    def _clone(self):
        clone = self.__class__()
        clone.select_columns = copy.copy(self.select_columns)
        clone.from_infos = copy.copy(self.from_infos)
        clone.where_infos = copy.copy(self.where_infos)
        clone.group_by_expressions = copy.copy(self.group_by_expressions)
        clone.limit_number = self.limit_number
        clone.offset_start = self.offset_start
        clone.order_by_infos = copy.copy(self.order_by_infos)
        return clone

    def _where(self, condition, parameters, conjunction):
        parameters = parameters or []
        clone = self._clone()
        # TODO: normalize to positional
        clone.where_infos.append(WhereInfo(condition, parameters, conjunction))
        return clone

    def _join(self, join_type, join_table, join_condition):
        # TODO: handle subqueries
        clone = self._clone()
        join_info = JoinInfo(join_type, join_table, join_condition)
        clone.join_infos.append(join_info)
        return clone
