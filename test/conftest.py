import pytest

# raise ValueError
xfail_value_error = pytest.mark.xfail(raises=ValueError, strict=True)
