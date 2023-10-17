import os
import shutil


def generate_package(pyi_root, ghidra_version, packages, stub_version="DEV"):
    setup_packages = ",".join('"{package}"'.format(package=package.split(".")[0]) for package in packages)
    setup_package_data = ",".join(
        '"{package}" : find_stub_files("{package}")'.format(package=package.split(".")[0]) for package in packages)
    setup_code = """
from setuptools import setup
import os

def find_stub_files(package):
    result = []
    for root, dirs, files in os.walk(package):
        for file in files:
            if file.endswith('.pyi'):
                file = os.path.relpath(os.path.join(root,file), start=package)
                result.append(file)
    return result

setup(name= 'ghidra-stubs',
version='{ghidra_version}.{stub_version}',
author='Tamir Bahar',
packages=[{packages}],
url="https://github.com/VDOO-Connected-Trust/ghidra-pyi-generator",
package_data={{{package_data}}},
long_description=open('README.md').read(),
long_description_content_type='text/markdown',
)
    """.format(ghidra_version=ghidra_version,
               stub_version=stub_version,
               packages=setup_packages,
               package_data=setup_package_data
               )

    ghidra_stub_folder = os.path.join(pyi_root, 'ghidra')
    shutil.copy2(os.path.join(pyi_root, 'ghidra_builtins.pyi'), ghidra_stub_folder)
    with open(os.path.join(pyi_root, 'setup.py'), 'w') as setup_file:
        setup_file.write(setup_code)

    # create an empty README file that is required for setup
    with open(os.path.join(pyi_root, 'README.md'), 'w'):
        pass

    print('Run `pip install {}` to install ghidra-stubs package'.format(pyi_root))
