django-paginator-rawqueryset
============================

A django paginator for RawQuerySet.  This allows you to pass a RawQuerySet into a custom paginator.
Supports mysql, sqlite, and postgresql.  Oracle is not supported.  

Put the paginator.py somewhere in your project folder and import it.  DO NOT copy it to django.core.

Example usage:

from paginator import Paginator
raw_query_set = some_model.objects.raw("SELECT * FROM some_model")
Paginator(raw_query_set,50)

You can also use this Paginator to paginate lists and querysets.  It detects the RawQuerySet
and calls RawQuerySetPaginator, but uses the default Django paginator otherwise.

In my tests, I'm getting up to 50% performance gains using this, mainly when paginating
a large complex query.  Don't bother using this for simple queries with a few pages,
stick to the default paginator and cast the RawQuerySet to a list.
