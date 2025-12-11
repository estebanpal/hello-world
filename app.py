import io
import base64
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from barcode import Code128
from barcode.writer import ImageWriter

from inventory import generate_kardex_workbook, get_item, update_stock, InventoryError

app = Flask(__name__)
app.secret_key = "kardex-demo-secret"
BASE_DIR = Path(__file__).resolve().parent


@app.context_processor
def inject_globals():
    return {"app_title": "Kardex de almacén"}


@app.route("/")
def index():
    items_file = BASE_DIR / "data" / "items.json"
    items = []
    if items_file.exists():
        import json

        items = json.loads(items_file.read_text())
    return render_template("index.html", items=items)


@app.route("/scan", methods=["POST"])
def scan():
    code = request.form.get("code", "").strip()
    action = request.form.get("action", "IN")
    quantity = request.form.get("quantity", "1")
    reference = request.form.get("reference", "Lectura de código de barras")
    try:
        quantity_int = int(quantity)
        item, balance = update_stock(code, quantity_int, action, reference)
        flash(f"Stock actualizado para {item['code']} ({item['name']}): saldo {balance}", "success")
    except (ValueError, InventoryError) as exc:
        flash(str(exc), "error")
    return redirect(url_for("index"))


@app.route("/label/<code>")
def label(code: str):
    try:
        item = get_item(code)
    except InventoryError as exc:
        flash(str(exc), "error")
        return redirect(url_for("index"))

    barcode_image = generate_barcode_image(item["code"])
    return render_template("label.html", item=item, barcode_image=barcode_image)


@app.route("/kardex.xlsx")
def kardex_export():
    wb = generate_kardex_workbook()
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return send_file(
        stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="kardex.xlsx",
    )


def generate_barcode_image(code: str) -> str:
    ean = Code128(code, writer=ImageWriter(), add_checksum=False)
    buffer = io.BytesIO()
    ean.write(buffer, options={"module_width": 0.3, "module_height": 10.0, "text": code})
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
