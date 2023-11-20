from sys import exit as _exit


if __name__ == '__main__':
    from ._internal.cli import main as _main
    try:
        from leads_emulation import Random as Controller
    except ImportError:
        raise EnvironmentError("At least one adapter has to be installed")
    _exit(_main(Controller("main")))
