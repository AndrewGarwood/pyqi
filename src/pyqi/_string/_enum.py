
from ..models import BaseStrEnum

# BaseEnum = BaseStrEnum # is not right color in 3.11 ... but should just do this
class BaseEnum(BaseStrEnum): ...