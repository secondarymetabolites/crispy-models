import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

long_description = read('README.md')

version_py = os.path.join('crispy_models', 'version.py')
version = read(version_py).strip().split('=')[-1].replace("'", "")

# No requirements so far
install_requires = []

tests_require = [
    "mockredispy-kblin",
    "pytest",
    "pytest-cov",
]

package_require = [
    "twine",
]

setup(name='crispy-models',
    version=version,
    install_requires=install_requires,
    tests_require=tests_require,
    author='Kai Blin',
    author_email='kblin@biosustain.dtu.dk',
    description='Shared code for CRISPy web service',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['crispy_models'],
    url='https://github.com/secondarymetabolites/crispy-models/',
    license='GNU Affero General Public License',
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
    ],
    extras_require={
        'testing': tests_require,
        'packaging': package_require,
    },
)
