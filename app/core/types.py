from typing import Annotated

from pydantic import StringConstraints

Password = Annotated[
    str,
    StringConstraints(
        min_length=8,
        strip_whitespace=True,
    ),
]
