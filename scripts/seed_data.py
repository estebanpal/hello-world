import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ITEMS_FILE = DATA_DIR / "items.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"

CATEGORIES = [
    "Estructura",
    "Tela",
    "Herrajes",
    "Eléctrico",
    "Pintura",
    "Fijaciones",
    "Consumible",
    "Seguridad",
    "Mecánico",
    "Adhesivos",
]

UNITS = ["unidad", "metro", "litro", "juego", "rollo", "kg", "par"]


def build_item(index: int) -> dict:
    category = CATEGORIES[index % len(CATEGORIES)]
    unit = UNITS[index % len(UNITS)]
    code = f"ITM{index:03d}"
    return {
        "code": code,
        "name": f"Ítem de almacén {index}",
        "category": category,
        "unit": unit,
        "stock": 25 + (index % 10) * 5,
        "location": f"Pasillo {(index % 5) + 1} - Estante {(index % 4) + 1}",
        "description": (
            "Componente utilizado en la fabricación de carpas igloo, módulos y hangares. "
            "Incluye especificaciones de calidad para montaje en proyectos modulares."
        ),
    }


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    items = [build_item(i) for i in range(1, 201)]
    ITEMS_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    if not TRANSACTIONS_FILE.exists():
        TRANSACTIONS_FILE.write_text("[]")
    print(f"Se generaron {len(items)} items en {ITEMS_FILE}")


if __name__ == "__main__":
    main()
