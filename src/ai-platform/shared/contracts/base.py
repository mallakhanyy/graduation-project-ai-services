"""Base class for all cross-service message contracts.

The .NET backend serialises JSON in camelCase, so every contract accepts
camelCase on input and emits camelCase on output (use ``by_alias=True``).
"""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ContractModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
