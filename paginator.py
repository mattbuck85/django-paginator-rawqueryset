from math import ceil

from django.core.paginator import Page
from django.db.models.query import RawQuerySet

from django.db import connections

class InvalidPage(Exception):
    pass

class PageNotAnInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass

class DefaultPaginator(object):
    def __init__(self, object_list, per_page, orphans=0, allow_empty_first_page=True):
        self.object_list = object_list
        self.per_page = per_page
        self.orphans = orphans
        self.allow_empty_first_page = allow_empty_first_page
        self._num_pages = self._count = None

    def validate_number(self, number):
        "Validates the given 1-based page number."
        try:
            number = int(number)
        except ValueError:
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                raise EmptyPage('That page contains no results')
        return number

    def get_page_objects(self,bottom,top):
        "RawQuerySetPaginator overrides this"
        return self.object_list[bottom:top]

    def page(self, number):
        "Returns a Page object for the given 1-based page number."
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        if top + self.orphans >= self.count:
            top = self.count
        return self._get_page(self.get_page_objects(bottom,top), number, self)

    def _get_page(self, *args, **kwargs):
        """ 
        Returns an instance of a single page.

        This hook can be used by subclasses to use an alternative to the
        standard :cls:`Page` object.
        """
        return Page(*args, **kwargs)

    def _get_count(self):
        "Returns the total number of objects, across all pages."
        if self._count is None:
            try:
                self._count = self.object_list.count()
            except (AttributeError, TypeError):
                # AttributeError if object_list has no count() method.
                # TypeError if object_list.count() requires arguments
                # (i.e. is of type list).
                self._count = len(self.object_list)
        return self._count
    count = property(_get_count)

    def _get_num_pages(self):
        "Returns the total number of pages."
        if self._num_pages is None:
            if self.count == 0 and not self.allow_empty_first_page:
                self._num_pages = 0
            else:
                hits = max(1, self.count - self.orphans)
                self._num_pages = int(ceil(hits / float(self.per_page)))
        return self._num_pages
    num_pages = property(_get_num_pages)

    def _get_page_range(self):
        """
        Returns a 1-based range of pages for iterating through within
        a te    mplate for loop.
        """
        return range(1, self.num_pages + 1)
    page_range = property(_get_page_range)

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

    def get_page_objects(self,bottom,top):
        rows_returned = top - bottom
        starting_at = bottom
        database_vendor = self.connection.vendor
        if database_vendor == 'mysql' or database_vendor == 'sqlite':
            query_with_limit = '%s LIMIT %s,%s' % (self.raw_query_set.raw_query,starting_at,rows_returned)
        elif database_vendor == 'postgresql':
            query_with_limit = '%s LIMIT %s OFFSET %s' % (self.raw_query_set.raw_query,rows_returned,starting_at)
        else:
            raise DatabaseNotSupportedException('%s is not supported by RawQuerySetPaginator' % database_vendor)
        return list(self.raw_query_set.model.objects.raw(query_with_limit,self.raw_query_set.params))

def Paginator(object_list,per_page,orphans=0,allow_empty_page_first=True):
    if isinstance(object_list,RawQuerySet):
        return RawQuerySetPaginator(object_list,per_page,orphans,allow_empty_page_first)
    else:
        return DefaultPaginator(object_list,per_page,orphans,allow_empty_page_first)
