from enum import Enum


class VectorDistance(str, Enum):
    COSINE = "Cosine"
    DOT = "Dot"
    EUCLID = "Euclid"