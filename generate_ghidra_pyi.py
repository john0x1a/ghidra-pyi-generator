# Generate .pyi's for Ghidra.
# @category: IDE Helpers
from __future__ import print_function
import importlib
import type_formatter

import ghidra
# Make this script work with the stubs in an IDE
try:
    from ghidra.ghidra_builtins import *
except:
    pass
from __main__ import askDirectory, askYesNo, getGhidraVersion, askString

from generate_stub_package import generate_package

import class_loader
import type_extractor
import pythonscript_handler
import helper

my_globals = globals().copy()


def main():
    # type: () -> None
    if not helper.are_docs_available():
        helper.extract_jsondoc()
    try:
        pyi_root = askDirectory('.pyi root directory', 'Select').getPath()
        print(pyi_root)

    except ghidra.util.exception.CancelledException:
        print('Generation canceled: No output directory selected.')
        return

    packages = ['ghidra']

    try:
        extra_packages = str(askString('Extra packages', 'Comma (,) separated packages')).split(",")
        packages.extend(extra_packages)
    except ghidra.util.exception.CancelledException:
        print('Extra package input canceled: Using default packages.')
        pass

    # First iteration to parse the modules and create the .pyi files
    for package in packages:
        class_loader.load_all_classes(prefix='{package}.'.format(package=package))
        try:
            extracted_package = type_extractor.Package.from_package(importlib.import_module(package))
            type_formatter.create_type_hints(pyi_root, extracted_package)
        except ImportError:
            print("Error importing package {package}".format(package=package))
            packages.remove(package)
            pass

    pythonscript_handler.create_mock(pyi_root, my_globals)

    package_version = "DEV"
    if isRunningHeadless():
        # We are running in an headless environment and this might be an automated CI build
        # so we try getting an extra argument that is supposed to be the git commit tag so the
        # package version is a combination  of the ghidra version and the version of the stub generating code
        try:
            package_version = askString("Package version", "Please specify package version")
        except:
            pass

    generate_package(pyi_root, getGhidraVersion(), packages=packages, stub_version=package_version)


if __name__ == '__main__':
    main()
