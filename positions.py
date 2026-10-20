from datetime import datetime

from pydantic import BaseModel, Field, ValidationError


class VehiclePosition(BaseModel):
    line: str = Field(alias="desi")
    direction: int = Field(alias="dir")
    operator: int = Field(alias="oper")
    vehicle: int = Field(alias="veh")
    timestamp: datetime = Field(alias="tst")
    latitude: float = Field(alias="lat")
    longitude: float = Field(alias="long")
    offset: int = Field(alias="dl")
    stop: int | None = None

    @property
    def delay(self) -> int:
        return -self.offset


class Message(BaseModel):
    vp: VehiclePosition = Field(alias="VP")


def parse_position(payload: bytes) -> VehiclePosition | None:
    try:
        return Message.model_validate_json(payload).vp
    except ValidationError:
        return None
