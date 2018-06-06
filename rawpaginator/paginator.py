from django.core.paginator import Page, Paginator as DefaultPaginator
from django.db.models.query import RawQuerySet
from django.db import connections


class DatabaseNotSupportedException(Exception):
    pass

class RawQuerySetPaginator(DefaultPaginator):
    """An efficient paginator for RawQuerySets.
    """
    _count = None

    def __init__(self, *args, **kwargs):
        super(RawQuerySetPaginator, self).__init__(*args, **kwargs)
        self.raw_query_set = self.object_list
        self.connection = connections[self.raw_query_set.db]

    def _get_count(self):
        if self._count is None:
            cursor = self.connection.cursor()
            count_query = """SELECT COUNT(*) FROM (%s) AS sub_query_for_count""" % self.raw_query_set.raw_query
            cursor.execute(count_query, self.raw_query_set.params)
            self._count = cursor.fetchone()[0]

        return self._count
    count = property(_get_count)

    def _get_limit_offset_query(self, limit, offset):
        """mysql, postgresql, and sqlite can all use this syntax
        """
        return """SELECT * FROM (%s) as sub_query_for_pagination
                LIMIT %s OFFSET %s""" % (self.raw_query_set.raw_query, limit, offset)
    
    mysql_getquery = _get_limit_offset_query
    postgresql_getquery = _get_limit_offset_query
    sqlite_getquery = _get_limit_offset_query

    def oracle_getquery(self, limit, offset):
        """Get the oracle query, but check the version first
           Query is only supported in oracle version >= 12.1
           TODO:TESTING
        """        
        major_version, minor_version = self.connection.oracle_version[0:2]
        if major_version < 12 or (major_version == 12 and minor_version < 1):
            raise DatabaseNotSupportedException('Oracle version must be 12.1 or higher')
            
        return """SELECT * FROM (%s) as sub_query_for_pagination 
                  OFFSET %s ROWS FETCH NEXT %s ROWS ONLY""" % (self.raw_query_set.raw_query, offset, limit)

    def firebird_getquery(self, limit, offset):##TODO:TESTING
        return """SELECT FIRST %s SKIP %s * 
                FROM (%s) as sub_query_for_pagination"""  % (limit, offset, self.raw_query_set.raw_query)

    def page(self, number):
        number = self.validate_number(number)
        offset = (number - 1 ) * self.per_page
        limit = self.per_page
        if offset + limit + self.orphans >= self.count:
            limit = self.count - offset
        database_vendor = self.connection.vendor

        try:
            query_with_limit = getattr(self, '%s_getquery' % database_vendor)(limit, offset)
        except AttributeError:
            raise DatabaseNotSupportedException('%s is not supported by RawQuerySetPaginator' % database_vendor)
        
        data = list(self.raw_query_set.model.objects.raw(query_with_limit, self.raw_query_set.params))
        return Page(data, number, self)

def Paginator(*args, **kwargs):
    if isinstance(object_list, RawQuerySet):
        return RawQuerySetPaginator(*args, **kwargs)
    else:
        return DefaultPaginator(*args, **kwargs)
