from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema class setting default global configurations for all Pydantic models."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )
