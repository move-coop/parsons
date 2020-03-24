import ast
import petl
import logging

logger = logging.getLogger(__name__)

# These are reserved words by Redshift and cannot be used as column names.
RESERVED_WORDS = ['AES128', 'AES256', 'ALL', 'ALLOWOVERWRITE', 'ANALYSE', 'ANALYZE', 'AND', 'ANY',
                  'ARRAY', 'AS', 'ASC', 'AUTHORIZATION', 'BACKUP', 'BETWEEN', 'BINARY',
                  'BLANKSASNULL', 'BOTH', 'BYTEDICT', 'BZIP2', 'CASE', 'CAST', 'CHECK', 'COLLATE',
                  'COLUMN', 'CONSTRAINT', 'CREATE', 'CREDENTIALS', 'CROSS', 'CURRENT_DATE',
                  'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURRENT_USER_ID',
                  'DEFAULT', 'DEFERRABLE', 'DEFLATE', 'DEFRAG', 'DELTA', 'DELTA32K', 'DESC',
                  'DISABLE', 'DISTINCT', 'DO', 'ELSE', 'EMPTYASNULL', 'ENABLE', 'ENCODE', 'ENCRYPT',
                  'ENCRYPTION', 'END', 'EXCEPT', 'EXPLICIT', 'FALSE', 'FOR', 'FOREIGN', 'FREEZE',
                  'FROM', 'FULL', 'GLOBALDICT256', 'GLOBALDICT64K', 'GRANT', 'GROUP', 'GZIP',
                  'HAVING', 'IDENTITY', 'IGNORE', 'ILIKE', 'IN', 'INITIALLY', 'INNER', 'INTERSECT',
                  'INTO', 'IS', 'ISNULL', 'JOIN', 'LEADING', 'LEFT', 'LIKE', 'LIMIT', 'LOCALTIME',
                  'LOCALTIMESTAMP', 'LUN', 'LUNS', 'LZO', 'LZOP', 'MINUS', 'MOSTLY13', 'MOSTLY32',
                  'MOSTLY8', 'NATURAL', 'NEW', 'NOT', 'NOTNULL', 'NULL', 'NULLS', 'OFF', 'OFFLINE',
                  'OFFSET', 'OLD', 'ON', 'ONLY', 'OPEN', 'OR', 'ORDER', 'OUTER', 'OVERLAPS',
                  'PARALLEL', 'PARTITION', 'PERCENT', 'PERMISSIONS', 'PLACING', 'PRIMARY', 'RAW',
                  'READRATIO', 'RECOVER', 'REFERENCES', 'RESPECT', 'REJECTLOG', 'RESORT', 'RESTORE',
                  'RIGHT', 'SELECT', 'SESSION_USER', 'SIMILAR', 'SOME', 'SYSDATE', 'SYSTEM',
                  'TABLE', 'TAG', 'TDES', 'TEXT255', 'TEXT32K', 'THEN', 'TIMESTAMP', 'TO', 'TOP',
                  'TRAILING', 'TRUE', 'TRUNCATECOLUMNS', 'UNION', 'UNIQUE', 'USER', 'USING',
                  'VERBOSE', 'WALLET', 'WHEN', 'WHERE', 'WITH', 'WITHOUT']


class RedshiftCreateTable(object):

    def __init__(self):

        pass

    def create_statement(self, tbl, table_name, padding=None, distkey=None, sortkey=None,
                         varchar_max=None, varchar_truncate=True, columntypes=None):
        # Generate a table create statement

        # Validate and rename column names if needed
        tbl.table = petl.setheader(tbl.table, self.column_name_validate(tbl.columns))

        if tbl.num_rows == 0:
            raise ValueError('Table is empty. Must have 1 or more rows.')

        mapping = self.generate_data_types(tbl)

        if padding:
            mapping['longest'] = self.vc_padding(mapping, padding)

        if varchar_max:
            mapping['longest'] = self.vc_max(mapping, varchar_max)

        if varchar_truncate:
            mapping['longest'] = self.vc_trunc(mapping)

        mapping['longest'] = self.vc_validate(mapping)

        # Add any provided column type overrides
        if columntypes:
            for i in range(len(mapping['headers'])):
                col = mapping['headers'][i]
                if columntypes.get(col):
                    mapping['type_list'][i] = columntypes[col]

        # Enclose in quotes
        mapping['headers'] = ['"{}"'.format(h) for h in mapping['headers']]

        return self.create_sql(table_name, mapping, distkey=distkey, sortkey=sortkey)

    def data_type(self, val, current_type):
        # Determine the Redshift data type of a given value

        try:
            # Convert to string to reevaluate data type
            t = ast.literal_eval(str(val))
        except ValueError:
            return 'varchar'
        except SyntaxError:
            return 'varchar'

        if type(t) in [int, float]:
            if (type(t) in [int] and current_type not in ['float', 'varchar']):

                # Make sure that it is a valid integer
                if not self.is_valid_integer(val):
                    return 'varchar'

                # Use smallest possible int type
                if (-32768 < t < 32767) and current_type not in ['int', 'bigint']:
                    return 'smallint'
                elif (-2147483648 < t < 2147483647) and current_type not in ['bigint']:
                    return 'int'
                else:
                    return 'bigint'
            if type(t) is float and current_type not in ['varchar']:
                return 'decimal'
        else:
            return 'varchar'

    def is_valid_integer(self, val):

        # Valid ints in python can contain an underscore, but Redshift can't. This
        # checks to see if there is an underscore in the value and turns it into
        # a varchar if so.
        try:
            if '_' in val:
                return False

        except TypeError:
            return True

        # If it has a leading zero, we should treat it as a varchar, since it is
        # probably there for a good reason (e.g. zipcode)
        if val.isdigit():
            if val[0] == '0':
                return False

        return True

    def generate_data_types(self, table):
        # Generate column data types

        longest, type_list = [], []

        cont = petl.records(table.table)

        # Populate empty values for the columns
        for col in table.columns:
            longest.append(0)
            type_list.append('')

        for row in cont:
            for i in range(len(row)):
                # NA is the csv null value
                if type_list[i] == 'varchar' or row[i] == 'NA':
                    pass
                else:
                    var_type = self.data_type(row[i], type_list[i])
                    type_list[i] = var_type
                # Calculate width
                if len(str(row[i]).encode('utf-8')) > longest[i]:
                    longest[i] = len(str(row[i]).encode('utf-8'))

        return {'longest': longest,
                'headers': table.columns,
                'type_list': type_list}

    def vc_padding(self, mapping, padding):
        # Pad the width of a varchar column

        return [int(c + (c * padding)) for c in mapping['longest']]

    def vc_max(self, mapping, columns):
        # Set the varchar width of a column to the maximum

        for c in columns:

            try:
                idx = mapping['headers'].index(c)
                mapping['longest'][idx] = 65535

            except KeyError as error:
                logger.error('Could not find column name provided.')
                raise error

        return mapping['longest']

    def vc_trunc(self, mapping):

        return [65535 if c > 65535 else c for c in mapping['longest']]

    def vc_validate(self, mapping):

        return [1 if c == 0 else c for c in mapping['longest']]

    def create_sql(self, table_name, mapping, distkey=None, sortkey=None):
        # Generate the sql to create the table

        statement = 'create table {} ('.format(table_name)

        for i in range(len(mapping['headers'])):
            if mapping['type_list'][i] == 'varchar':
                statement = (statement + '\n  {} varchar({}),').format(str(mapping['headers'][i])
                                                                       .lower(),
                                                                       str(mapping['longest'][i]))
            else:
                statement = (statement + '\n  ' + '{} {}' + ',').format(str(mapping['headers'][i])
                                                                        .lower(),
                                                                        mapping['type_list'][i])

        statement = statement[:-1] + ') '

        if distkey:
            statement += '\ndistkey({}) '.format(distkey)

        if sortkey:
            statement += '\nsortkey({})'.format(sortkey)

        statement += ';'

        return statement

    def column_name_validate(self, columns):
        # Validate the column names and rename if not valid

        clean_columns = []

        for idx, c in enumerate(columns):

            # Lowercase
            c = c.lower()

            # Remove spaces. Technically allowed with double quotes
            # but I think that it is bad practice.
            c = c.replace(' ', '')

            # if column is an empty string, replace with 'col_INDEX'
            if c == '':
                logger.info(f'Column is an empty string. Renaming column.')
                c = f'col_{idx}'

            # If column is a reserved word, replace with 'col_INDEX'. Technically
            # you can allow these with quotes, but I think that it is bad practice
            if c.upper()in RESERVED_WORDS:
                logger.info(f'{c} is a Redshift reserved word. Renaming column.')
                c = f'col_{idx}'

            # If column name begins with an integer, preprent with 'x_'
            if c[0].isdigit():
                logger.info(f'{c} begins with digit. Renaming column.')
                c = f'x_{c}'

            # If column name length is greater than 120 characters, truncate.
            # Technically, you can have up to 127 bytes, which might allow
            # for a few more characters, but playing it safe.
            if len(c) > 120:
                logger.info(f'Column {c[:10]}... too long. Truncating column name.')
                c = c[:120]

            clean_columns.append(c)

        return clean_columns
