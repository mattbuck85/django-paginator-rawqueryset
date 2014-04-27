from math import ceil

from django.core.paginator import Page, Paginator as DefaultPaginator
from django.db.models.query import RawQuerySet

from django.db import connections

class DatabaseNotSupportedException(Exception):
    pass

class RawQuerySetPaginator(DefaultPaginator):
    "An efficient paginator for RawQuerySets."
    def __init__(self,object_list,per_page,orphans=0,allow_empty_page_first=True):
        super(RawQuerySetPaginator,self).__init__(object_list,per_page,orphans,allow_empty_page_first)
        self.raw_query_set = self.object_list
        self.connection = connections[self.raw_query_set.db]

    def _get_count(self):
        if self._count is None:
            cursor = self.connection.cursor()
            count_query = 'SELECT COUNT(*) FROM (%s) AS sub_query_for_count' % self.raw_query_set.raw_query
            cursor.execute(count_query,self.raw_query_set.params)
            self._count = cursor.fetchone()[0]
        return self._count
    count = property(_get_count)

    def page(self,number):
        number = self.validate_number(number)
        offset = (number -1 ) * self.per_page
        limit = self.per_page
        if limit + self.orphans >= self.count:
            limit = self.count
        database_vendor = self.connection.vendor
        if database_vendor in ('mysql','postgresql','sqlite'):
            query_with_limit = '%s LIMIT %s OFFSET %s' % (self.raw_query_set.raw_query,limit,offset)
        else:
            raise DatabaseNotSupportedException('%s is not supported by RawQuerySetPaginator' % database_vendor)
        return Page(list(self.raw_query_set.model.objects.raw(query_with_limit,self.raw_query_set.params)), number, self)

def Paginator(object_list,per_page,orphans=0,allow_empty_page_first=True):
    if isinstance(object_list,RawQuerySet):
        return RawQuerySetPaginator(object_list,per_page,orphans,allow_empty_page_first)
    else:
        return DefaultPaginator(object_list,per_page,orphans,allow_empty_page_first)
