from PIL import Image

from quality_assessment.blur_detection import blur_score
from quality_assessment.brightness_detection import brightness_score
from shared.contracts.vision_contract import ImageQualityReport

W_SHARPNESS, W_BRIGHTNESS, W_RESOLUTION = 0.5, 0.3, 0.2
RESOLUTION_REFERENCE = 512  # min side considered fully sufficient

RETAKE_ADVICE: dict[str, dict[str, str]] = {
    "blurry": {
        "en": "The photo is blurry. Hold the phone steady and take it closer, focusing on the problem area.",
        "ar": "الصورة غير واضحة، ثبّت الهاتف والتقط الصورة من مسافة أقرب مع التركيز على مكان المشكلة.",
    },
    "too_dark": {
        "en": "The photo is too dark. Take it in daylight or better lighting.",
        "ar": "الصورة مظلمة جداً، التقط الصورة في ضوء النهار أو بإضاءة أفضل.",
    },
    "too_bright": {
        "en": "The photo is overexposed. Avoid direct sun or flash and try again.",
        "ar": "الصورة شديدة السطوع، تجنب الضوء المباشر أو الفلاش وأعد التصوير.",
    },
    "low_resolution": {
        "en": "The photo resolution is low. Move closer to the problem area and retake it.",
        "ar": "دقة الصورة منخفضة، اقترب من مكان المشكلة والتقط صورة أوضح.",
    },
    "invalid_file": {
        "en": "The file could not be read as an image. Please upload a JPG or PNG photo.",
        "ar": "تعذّر قراءة الملف كصورة، يرجى رفع صورة بصيغة JPG أو PNG.",
    },
}


def assess_quality(image_key: str, image: Image.Image, threshold: float = 0.45) -> ImageQualityReport:
    sharp, is_blurry = blur_score(image)
    bright, too_dark, too_bright = brightness_score(image)
    res = min(min(image.size) / RESOLUTION_REFERENCE, 1.0)

    issues: list[str] = []
    if is_blurry:
        issues.append("blurry")
    if too_dark:
        issues.append("too_dark")
    if too_bright:
        issues.append("too_bright")
    if res < 0.5:
        issues.append("low_resolution")

    score = W_SHARPNESS * sharp + W_BRIGHTNESS * bright + W_RESOLUTION * res
    return ImageQualityReport(
        image_key=image_key,
        width=image.width,
        height=image.height,
        blur_score=round(sharp, 4),
        brightness_score=round(bright, 4),
        quality_score=round(score, 4),
        # Blur is a hard failure: a diagnosis from an out-of-focus photo is unreliable.
        is_acceptable=score >= threshold and "blurry" not in issues,
        issues=issues,
    )


def advice_for(issues: list[str], language: str = "ar") -> list[str]:
    lang = language if language in ("ar", "en") else "en"
    seen: list[str] = []
    for issue in issues:
        text = RETAKE_ADVICE.get(issue, {}).get(lang)
        if text and text not in seen:
            seen.append(text)
    return seen