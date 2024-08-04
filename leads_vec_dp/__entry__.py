from argparse import ArgumentParser as _ArgumentParser
from sys import exit as _exit

from leads_vec_dp.run import run


def __entry__() -> None:
    parser = _ArgumentParser(prog="LEADS VeC DP",
                             description="Lightweight Embedded Assisted Driving System VeC Data Processor",
                             epilog="GitHub: https://github.com/ProjectNeura/LEADS")
    parser.add_argument("workflow", help="specify a workflow file")
    args = parser.parse_args()
    _exit(run(args.workflow))
