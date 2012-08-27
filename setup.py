from setuptools import setup, find_packages

readme_file = 'README.rst'

setup(
    name='datafilters',
    version='0.3.1',
    packages=find_packages('.'),
    package_data = {'': [
        'locale/*/LC_MESSAGES/django.po',
        'locale/*/LC_MESSAGES/django.mo',
    ]},

    # Metadata
    author='Nikolay Zakharov',
    author_email='nikolay@desh.su',
    url = 'https://github.com/freevoid/django-datafilters',
    description='Neat QuerySet filter for django apps with filterforms based on django forms',
    long_description=open(readme_file).read(),
    keywords='django filter datafilter queryset',
    license = 'MIT',
    install_requires=['django>=1.3'],
    extras_require={
        'extra_specs': ['forms-extras'],
    },
    classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Framework :: Django',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
    ],
)
