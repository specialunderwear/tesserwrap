import os
import sys
from setuptools import setup, Extension

import multiprocessing
import distutils.util as du_util

pkgdirs = []
incdirs = ['/usr/local/include']
libdirs = ['/usr/local/lib']

def append_env(L, e):
    v = os.environ.get(e)
    if v and os.path.exists(v):
        L.append(v)

append_env(pkgdirs, "LIBTESSERACT")

unprocessed = []
for arg in sys.argv[1:]:
    if "=" in arg and arg.startswith("--with-libtesseract"):
        pkgdirs.append(arg.split("=", 1)[1])
        continue
    unprocessed.append(arg)
sys.argv[1:] = unprocessed

for pkgdir in pkgdirs:
    incdirs.append(os.path.join(pkgdir, "include"))
    libdirs.append(os.path.join(pkgdir, "lib"))


# Library locator function
# Looks to see which library is available to link against
def check_lib_by_name(lib_name, search_path=None):
    s_path = ""
    platform_opts = ""
    if search_path:
        for path in search_path:
            s_path = s_path + "-L%s " % path

    # OSX specific (From: jmel - Tesserwrap: #11)
    if "macosx" in du_util.get_platform():
        platform_opts = "-arch x86_64 -execute -macosx_version_min 10.6 -pie -lm -lpthread -lcrt1.o"

    return os.system('ld %s %s -l%s' % (s_path, platform_opts, lib_name)) == 0


def find_closest_libname(lib_names, search_path=None):
    for lib_name in lib_names:
        if check_lib_by_name(lib_name, search_path):
            return lib_name
    raise Exception(
        "Cannot find Tesseract via ldconfig, confirm it is installed.")


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

tesseract_possible_names = ['tesseract_api', 'tesseract']
tesseract_lib_name = find_closest_libname(
    tesseract_possible_names,
    libdirs)

tesser_cpp = Extension(
    'libtesserwrap',
    include_dirs=incdirs,
    libraries=[tesseract_lib_name],
    library_dirs=libdirs,
    sources=[
        'tesserwrap/cpp/tesseract_ext.cpp',
        'tesserwrap/cpp/tesseract_wrap.cpp'],
    depends=[
        'tesserwrap/cpp/tesseract_wrap.cpp',
        'tesserwrap/cpp/tesseract_wrap.h',
        'tesserwrap/cpp/tesseract_ext.cpp',
        'tesserwrap/cpp/tesseract_ext.h'
    ],
)

if os.environ.get('READTHEDOCS', None) == 'True':
    extensions = None
else:
    extensions = [tesser_cpp]

setup(
    name="tesserwrap",
    version="0.1.6",
    author="Greg Jurman, and others",
    author_email="gdj2214@rit.edu",
    description=("Basic python bindings to the Tesseract C++ API"),
    license="Apache License 2.0",
    keywords="tesseract ocr cpp",
    url="https://github.com/gregjurman/tesserwrap",
    packages=['tesserwrap'],
    zip_safe=False,
    ext_modules=extensions,
    long_description=read('README'),
    tests_require=['nose', 'Pillow'],
    test_suite="nose.collector",
    classifiers=[
        "Topic :: Scientific/Engineering :: Image Recognition",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],
)
