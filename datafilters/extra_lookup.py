class Extra(object):

    def __init__(self, where=None, tables=None):
        self.where = where if where is not None else []
        self.tables = tables if tables is not None else []

    def is_empty(self):
        return self.where or self.tables

    def add(self, extra):
        self.where.extend(extra.where)
        self.tables.extend(extra.tables)
        return self

    def as_kwargs(self):
        return {
            'where': self.where,
            'tables': self.tables,
        }

    # little magic
    __iadd__ = add
    __bool__ = __nonzero__ = is_empty
