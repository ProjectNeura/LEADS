from setuptools import find_packages, setup


def find_certain_packages(prefix: str) -> list[str]:
    return list(map(lambda p: prefix + "." + p, find_packages(prefix)))


SHORT_DESCRIPTION = "Lightweight Embedded Assisted Driving System"
with open("./README.md", "r") as f:
    LONG_DESCRIPTION = f.read()
AUTHOR_EMAIL = "central@projectneura.org"

setup(
    name="leads",
    version="0.0.1",
    author="ProjectNeura",
    author_email=AUTHOR_EMAIL,
    description=SHORT_DESCRIPTION,
    license='Apache License 2.0',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_certain_packages("leads"),
    install_requires=[]
)

setup(
    name="leads-dashboard",
    version="0.0.1",
    author="ProjectNeura",
    author_email=AUTHOR_EMAIL,
    description=SHORT_DESCRIPTION,
    license='Apache License 2.0',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_certain_packages("leads_dashboard"),
    install_requires=["dearpygui", "leads"]
)

setup(
    name="leads-emulation",
    version="0.0.1",
    author="ProjectNeura",
    author_email=AUTHOR_EMAIL,
    description=SHORT_DESCRIPTION,
    license='Apache License 2.0',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_certain_packages("leads_emulation"),
    install_requires=["leads"]
)

setup(
    name="leads-vec",
    version="0.0.1",
    author="ProjectNeura",
    author_email=AUTHOR_EMAIL,
    description=SHORT_DESCRIPTION,
    license='Apache License 2.0',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectNeura/LEADS",
    packages=find_certain_packages("leads_vec"),
    install_requires=["keyboard", "leads", "leads-dashboard", "leads-emulation"]
)
