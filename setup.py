from setuptools import find_packages, setup

with open("./README.md") as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="leads",
    version="0.7.3",
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
        "leads_gui": [
            "assets/leads-theme.json", "assets/icons/battery-black.png", "assets/icons/battery-red.png",
            "assets/icons/battery-white.png", "assets/icons/brake-black.png", "assets/icons/brake-red.png",
            "assets/icons/brake-white.png", "assets/icons/ecs-black.png", "assets/icons/ecs-red.png",
            "assets/icons/ecs-white.png", "assets/icons/engine-black.png", "assets/icons/engine-red.png",
            "assets/icons/engine-white.png", "assets/icons/high-beam-black.png", "assets/icons/high-beam-red.png",
            "assets/icons/high-beam-white.png", "assets/icons/light-black.png", "assets/icons/light-red.png",
            "assets/icons/light-white.png", "assets/icons/motor-black.png", "assets/icons/motor-red.png",
            "assets/icons/motor-white.png", "assets/icons/speed-black.png", "assets/icons/speed-red.png",
            "assets/icons/speed-white.png"
        ],
        "leads_vec": ["_bootloader/leads_vec.service.sh"],
        "leads_vec_rc": ["_bootloader/leads_vec_rc.service.sh", "config.json"]
    },
    include_package_data=True,
    install_requires=["numpy"]
)
