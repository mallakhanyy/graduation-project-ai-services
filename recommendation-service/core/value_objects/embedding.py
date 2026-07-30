from dataclasses import dataclass

@dataclass(frozen=True)
class Embeddding:
    vector : tuple[list,...]