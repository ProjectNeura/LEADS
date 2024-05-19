from setuptools import find_packages, setup

with open("README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="leads",
    version="0.8.31",
    python_requires=">=3.12",
    author="ProjectNeura",
    author_email="central@projectneura.org",
    description="Lightweight Embedded Assisted Driving System",
    license="Apache License 2.0",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_packages(),
    package_data={
        "leads_audio": ["assets/*"],
        "leads_gui": ["assets/*", "assets/icons/*"],
        "leads_vec": ["_bootloader/leads-vec.service.sh"]
    },
    include_package_data=True,
    install_requires=["numpy", "pandas"]
)
