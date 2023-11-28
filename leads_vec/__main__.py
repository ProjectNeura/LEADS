from sys import argv as _argv, exit as _exit


if __name__ == '__main__':
    try:
        from leads_emulation import Random as Controller
    except ImportError:
        raise EnvironmentError("At least one adapter has to be installed")
    if "remote" in _argv:
        from .remote import remote as _main

        _main()
    else:
        from .cli import main as _main

        _exit(_main(Controller("main")))
