from setuptools import find_packages, setup

with open("./README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="leads",
    version="0.6.1",
    author="ProjectNeura",
    author_email="central@projectneura.org",
    description="Lightweight Embedded Assisted Driving System",
    license="Apache License 2.0",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_packages(),
    package_data={
        "leads_gui": ["leads-theme.json"],
        "leads_vec": ["_bootloader/leads_vec.service.sh"],
        "leads_vec_rc": ["_bootloader/leads_vec_rc.service.sh", "config.json"]
    },
    include_package_data=True,
    install_requires=["numpy"]
)
