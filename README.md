django-paginator-rawqueryset
============================

A django paginator for RawQuerySet.  This allows you to pass a RawQuerySet into a custom paginator.
Supports mysql, sqlite, and postgresql.  Oracle is not supported.  

In my tests, I'm getting up to 50% performance gains using this, mainly when paginating
a large complex query.  Don't bother using this for simple queries with a few pages,
stick to the default paginator and cast the RawQuerySet to a list.

Tested with Django 1.4.10 and Python 2.7, but should work with all versions after 1.4.
Not tested with Python 3.
