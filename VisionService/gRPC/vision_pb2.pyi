from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PredictRequest(_message.Message):
    __slots__ = ("request_id", "image_data", "image_url", "filename")
    REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    IMAGE_DATA_FIELD_NUMBER: _ClassVar[int]
    IMAGE_URL_FIELD_NUMBER: _ClassVar[int]
    FILENAME_FIELD_NUMBER: _ClassVar[int]
    request_id: str
    image_data: bytes
    image_url: str
    filename: str
    def __init__(self, request_id: _Optional[str] = ..., image_data: _Optional[bytes] = ..., image_url: _Optional[str] = ..., filename: _Optional[str] = ...) -> None: ...

class HealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class PredictResponse(_message.Message):
    __slots__ = ("status", "problem", "confidence", "severity", "recommendation", "explanation", "repair_steps", "timestamp")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    PROBLEM_FIELD_NUMBER: _ClassVar[int]
    CONFIDENCE_FIELD_NUMBER: _ClassVar[int]
    SEVERITY_FIELD_NUMBER: _ClassVar[int]
    RECOMMENDATION_FIELD_NUMBER: _ClassVar[int]
    EXPLANATION_FIELD_NUMBER: _ClassVar[int]
    REPAIR_STEPS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    status: str
    problem: str
    confidence: str
    severity: str
    recommendation: str
    explanation: str
    repair_steps: _containers.RepeatedScalarFieldContainer[str]
    timestamp: str
    def __init__(self, status: _Optional[str] = ..., problem: _Optional[str] = ..., confidence: _Optional[str] = ..., severity: _Optional[str] = ..., recommendation: _Optional[str] = ..., explanation: _Optional[str] = ..., repair_steps: _Optional[_Iterable[str]] = ..., timestamp: _Optional[str] = ...) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("status", "service", "version", "model_loaded", "binary_classifier_loaded", "timestamp")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SERVICE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    MODEL_LOADED_FIELD_NUMBER: _ClassVar[int]
    BINARY_CLASSIFIER_LOADED_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    status: str
    service: str
    version: str
    model_loaded: bool
    binary_classifier_loaded: bool
    timestamp: str
    def __init__(self, status: _Optional[str] = ..., service: _Optional[str] = ..., version: _Optional[str] = ..., model_loaded: bool = ..., binary_classifier_loaded: bool = ..., timestamp: _Optional[str] = ...) -> None: ...
