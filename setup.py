from setuptools import setup

from rawpaginator.version import __version__

description = 'Paginator for django RawQuerySets.  Functions similar to the built-in Paginator'

setup(name='django-paginator-rawqueryset',
      packages=['rawpaginator'],
      version=__version__,
      description=description,
      author='Matt Buck',
      author_email='seamusmb@gmail.com',
      url='https://github.com/seamusmb/django-paginator-rawqueryset',
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License"],
      )
