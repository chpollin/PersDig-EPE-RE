"""
Stub für einen ALTO/PAGE‑Parser.

Dieses Modul enthält Datenklassen und eine unvollständige Funktion `parse_alto`, die
veranschaulicht, wie ein Importer für ALTO/PAGE‑XML aufgebaut werden könnte.
Die echte Implementierung muss die in der Spezifikation beschriebenen
Modifikationen von eScriptorium (z. B. Leerzeichen statt Kommas) berücksichtigen
und Koordinaten korrekt normalisieren.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Token:
    id: str
    text: str
    position: int
    bbox: Dict[str, float]
    baseline: Optional[List[int]] = None


@dataclass
class Section:
    id: str
    order_no: int
    type: str
    tokens: List[Token] = field(default_factory=list)


@dataclass
class Witness:
    id: str
    siglum: str
    label: str
    sections: List[Section] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


def parse_alto(alto_xml_path: str) -> Witness:
    """
    Liest eine ALTO/PAGE‑XML‑Datei ein und wandelt sie in ein Witness‑Objekt um.
    Diese Funktion ist ein Platzhalter und führt keine echte XML‑Verarbeitung durch.

    Args:
        alto_xml_path: Pfad zur ALTO- oder PAGE-Datei.

    Returns:
        Ein Witness‑Objekt mit Dummy‑Daten.
    """
    # TODO: XML parsen (z. B. mit ElementTree), Baselines extrahieren und in
    # Token‑Koordinaten umwandeln. Leerzeichen in Koordinaten normalisieren.

    # Beispielhafte Dummy‑Daten
    witness = Witness(
        id="w_demo",
        siglum="MS_DUMMY",
        label="Demo Witness",
        metadata={"language": "la", "source": alto_xml_path},
    )
    section = Section(id="sec_demo", order_no=1, type="page")
    section.tokens.append(
        Token(
            id="tok_demo1",
            text="lorem",
            position=1,
            bbox={"x": 0, "y": 0, "width": 100, "height": 20},
        )
    )
    section.tokens.append(
        Token(
            id="tok_demo2",
            text="ipsum",
            position=2,
            bbox={"x": 110, "y": 0, "width": 120, "height": 20},
        )
    )
    witness.sections.append(section)
    return witness