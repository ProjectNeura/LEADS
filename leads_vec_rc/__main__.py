from os import system as _system, chdir as _chdir
from os.path import abspath as _abspath

if __name__ == '__main__':
    _chdir(_abspath(__file__)[:-12])
    _system("uvicorn cli:app --reload")
