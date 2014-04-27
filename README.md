django-paginator-rawqueryset
============================

A django paginator for RawQuerySet.  This allows you to pass a RawQuerySet into a custom paginator.
Supports mysql, sqlite, and postgresql.  Oracle is not supported. 

Installation
============

Installing the dev version:

    pip install git+git://github.com/seamusmb/django-paginator-rawqueryset.git

Add 'rawpaginator' to your INSTALLED_APPS in settings.py

Usage
=====

if you want a Paginator that can work with querysets, lists, and rawquerysets, do this:

```python
   from rawpaginator.paginator import Paginator
   raw_qs = some_model.objects.raw('''SELECT * FROM some_model''')
   p = Paginator(raw_qs,50)
   p.page(1)
```

or if you just want the RawQuerySetPaginator, you can do this:

```python
   from rawpaginator.paginator import RawQuerySetPaginator
   raw_qs = some_model.objects.raw('''SELECT * FROM some_model''')
   p = RawQuerySetPaginator(raw_qs,50)
   p.page(1)
```
In my tests, I'm getting up to 50% performance gains using this, mainly when paginating
a large complex query.  Don't bother using this for simple queries with a few pages,
stick to the default paginator and cast the RawQuerySet to a list.

Tested with Django 1.4.10 and Python 2.7, but should work with all versions after 1.4.
Not tested with Python 3.
