from setuptools import find_packages, setup

with open("./README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="leads",
    version="0.0.10",
    author="ProjectNeura",
    author_email="central@projectneura.org",
    description="Lightweight Embedded Assisted Driving System",
    license='Apache License 2.0',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_packages(),
    package_data={
        "leads_dashboard": ["_font/OpenSans-Regular.ttf"]
    },
    include_package_data=True,
    install_requires=["numpy"]
)
