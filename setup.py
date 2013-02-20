from setuptools import setup, find_packages
from mezzanine_recipes import __version__

setup(
    name="mezzanine-recipes",
    version=__version__,
    description='Recipe blog posts for Mezzanine CMS',
    long_description=open("README.rst").read(),
    author='Thomas Jetzinger',
    author_email='thomas@jetzinger.com',
    url='https://github.com/tjetzinger/mezzanine-recipes',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django==1.4.4',
        'Mezzanine==1.4.1',
        'django-tastypie==0.9.12',
        'South==0.7.6',
        'uuid==1.30',
        'html2text==3.200.3',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        "Programming Language :: Python",
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
