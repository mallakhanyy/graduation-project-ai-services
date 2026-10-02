from enum import Enum


class Category(str, Enum):
    IRRIGATION = "irrigation"
    DRAINAGE = "drainage"
    WATER_QUALITY = "water_quality"
    MAINTENANCE = "maintenance"
    RAINWATER_HARVESTING = "rainwater_harvesting"
    SOIL = "soil"
    WATER_MANAGEMENT = "water_management"