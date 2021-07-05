import setuptools
import versioneer

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    package_requirements = fh.read()

setuptools.setup(
    name="cyclemap",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Floris Van den Abeele",
    description="Display cycle tours and social media content on a map",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': [
        'import_masto = cyclemap.scripts.import_masto:cli',
    ]},
    install_requires=package_requirements,
    include_package_data=True,  # include files listed in MANIFEST.in
    python_requires='~=3.9',
)
