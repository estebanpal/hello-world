import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ITEMS_FILE = DATA_DIR / "items.json"
TRANSACTIONS_FILE = DATA_DIR / "transactions.json"


class InventoryError(Exception):
    """Errores para operaciones de inventario."""


def load_items() -> List[Dict]:
    if not ITEMS_FILE.exists():
        raise InventoryError("No se encontró el archivo de items. Ejecute scripts/seed_data.py")
    return json.loads(ITEMS_FILE.read_text())


def save_items(items: List[Dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ITEMS_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def load_transactions() -> List[Dict]:
    if TRANSACTIONS_FILE.exists():
        return json.loads(TRANSACTIONS_FILE.read_text())
    return []


def save_transactions(transactions: List[Dict]):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    TRANSACTIONS_FILE.write_text(json.dumps(transactions, ensure_ascii=False, indent=2))


def get_item(code: str) -> Dict:
    items = load_items()
    for item in items:
        if item["code"].lower() == code.lower():
            return item
    raise InventoryError(f"El ítem con código {code} no existe")


def update_stock(code: str, quantity: int, action: str, reference: str = "Lectura de código") -> Tuple[Dict, int]:
    if quantity <= 0:
        raise InventoryError("La cantidad debe ser mayor que cero")
    if action not in {"IN", "OUT"}:
        raise InventoryError("La acción debe ser IN o OUT")

    items = load_items()
    item = None
    for entry in items:
        if entry["code"].lower() == code.lower():
            item = entry
            break
    if item is None:
        raise InventoryError(f"El ítem con código {code} no existe")

    delta = quantity if action == "IN" else -quantity
    new_stock = item["stock"] + delta
    if new_stock < 0:
        raise InventoryError("La salida supera el stock disponible")

    item["stock"] = new_stock
    save_items(items)

    transactions = load_transactions()
    movement = {
        "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "code": item["code"],
        "action": action,
        "quantity": quantity,
        "balance": new_stock,
        "reference": reference,
    }
    transactions.append(movement)
    save_transactions(transactions)
    return item, new_stock


def generate_kardex_workbook() -> Workbook:
    items = load_items()
    transactions = load_transactions()

    wb = Workbook()
    ws_items = wb.active
    ws_items.title = "Items"
    ws_items.append(["Código", "Nombre", "Categoría", "Unidad", "Stock", "Ubicación", "Descripción"])
    for item in items:
        ws_items.append(
            [
                item["code"],
                item["name"],
                item["category"],
                item["unit"],
                item["stock"],
                item["location"],
                item["description"],
            ]
        )
    for cell in ws_items[1]:
        cell.font = Font(bold=True)
    ws_items.freeze_panes = "A2"

    ws_mov = wb.create_sheet("Movimientos")
    ws_mov.append(["Fecha", "Código", "Acción", "Cantidad", "Saldo", "Referencia"])
    for mov in transactions:
        ws_mov.append(
            [
                mov.get("timestamp"),
                mov.get("code"),
                "Ingreso" if mov.get("action") == "IN" else "Salida",
                mov.get("quantity"),
                mov.get("balance"),
                mov.get("reference", ""),
            ]
        )
    for cell in ws_mov[1]:
        cell.font = Font(bold=True)
    ws_mov.freeze_panes = "A2"
    for col in ws_mov.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        ws_mov.column_dimensions[col[0].column_letter].width = max(12, min(max_len + 2, 35))

    ws_items.auto_filter.ref = f"A1:G{len(items)+1}"
    ws_mov.auto_filter.ref = f"A1:F{len(transactions)+1}"
    ws_mov["A1"].alignment = Alignment(horizontal="center")

    return wb
