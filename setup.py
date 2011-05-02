from setuptools import setup, find_packages

readme_file = 'README.rst'

setup(
    name='datafilters',
    version='0.1.0',
    packages=find_packages('.'),

    # Metadata
    author='Nikolay Zakharov',
    author_email='nikolay@desh.su',
    url = 'https://github.com/freevoid/django-datafilters',
    description='Neat QuerySet filter for django apps with filterforms based on django forms',
    long_description=open(readme_file).read(),
    keywords='django filter datafilter queryset',
    license = 'MIT',
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
    ],
)
