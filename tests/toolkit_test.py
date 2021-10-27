import pytest
from logging import DEBUG, basicConfig


from sudan.tools import Toolkit



def test_toolkit_lazy():
    tk = Toolkit()

    print(tk.parallel)
    print(tk.parallel)


def test_load_all():
    tk = Toolkit()
    tk.init_all()



if __name__ == '__main__':
    basicConfig(level=DEBUG)
    pytest.main(['-s'])