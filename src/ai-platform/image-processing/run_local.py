import sys
from shared.configuration.settings import get_settings
from shared.contracts.vision_contract import VisionRequest
from services.vision_service import build_vision_service

path = sys.argv[1]
settings = get_settings()
settings.enable_captioning = False

service = build_vision_service(settings)
data = open(path, "rb").read()
request = VisionRequest(query_id="local-test", bucket="", image_keys=[path])
result = service.analyze(request, [(path, data)])
print(result.model_dump_json(indent=2, by_alias=True))