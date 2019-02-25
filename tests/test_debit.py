import pytest
from littlecoins.transactions import list_of_files


def test_list_maker():
    path_to_data=r"data/"
    assert isinstance(list_of_files() , list)==True