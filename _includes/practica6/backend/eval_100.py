import os
import time
import uuid
import random
from datetime import datetime

import requests
import pandas as pd

from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001/led-agent")
N_RUNS = int(os.getenv("N_RUNS", "100"))
RANDOM_SEED = int(os.getenv("RANDOM_SEED", "42"))

INPUT_PRICE_PER_1M = float(os.getenv("INPUT_PRICE_PER_1M", "0"))
OUTPUT_PRICE_PER_1M = float(os.getenv("OUTPUT_PRICE_PER_1M", "0"))

CSV_OUTPUT = "resultados_llm_led_raw.csv"
XLSX_OUTPUT = "instrumento_supervision_llm_led.xlsx"

random.seed(RANDOM_SEED)

DATASET = [
    ("enciende el led", "on"),
    ("prende el led", "on"),
    ("activa la luz del prototipo", "on"),
    ("enciende la salida digital", "on"),
    ("quiero que el led quede prendido", "on"),
    ("puedes prender la luz", "on"),

    ("apaga el led", "off"),
    ("desactiva el led", "off"),
    ("quita la luz", "off"),
    ("apaga la salida digital", "off"),
    ("quiero que el led quede apagado", "off"),
    ("desconecta la señal de luz", "off"),

    ("explícame qué es MQTT", "none"),
    ("qué es un led", "none"),
    ("cuál es la diferencia entre mqtt y http", "none"),
    ("no enciendas el led", "none"),
    ("no lo prendas todavía", "none"),
    ("mañana enciende el led", "none"),
    ("si puedes, dime cómo funciona un esp32", "none"),
    ("revisa el estado del led", "none"),
]


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        (input_tokens / 1_000_000) * INPUT_PRICE_PER_1M
        + (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_1M
    )


def run_single_test(index: int):
    prompt, expected_action = random.choice(DATASET)
    trial_id = str(uuid.uuid4())

    payload = {"prompt": prompt, "expected_action": expected_action}
    start = time.perf_counter()

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=240)
        api_elapsed_ms = (time.perf_counter() - start) * 1000
        data = response.json()

        llm_action = data.get("llm_action")
        prompt_eval_count = int(data.get("prompt_eval_count", 0) or 0)
        eval_count = int(data.get("eval_count", 0) or 0)

        return {
            "trial_index": index,
            "trial_id": trial_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "prompt": prompt,
            "expected_action": expected_action,
            "llm_action": llm_action,
            "is_correct": expected_action == llm_action,
            "schema_valid": bool(data.get("schema_valid", False)),
            "mqtt_published": bool(data.get("mqtt_published", False)),
            "architecture_success": bool(data.get("architecture_success", False)),
            "api_elapsed_ms_client": api_elapsed_ms,
            "api_elapsed_ms_backend": data.get("api_elapsed_ms"),
            "backend_elapsed_ms": data.get("backend_elapsed_ms"),
            "ollama_elapsed_ms": data.get("ollama_elapsed_ms"),
            "mqtt_publish_ms": data.get("mqtt_publish_ms"),
            "prompt_eval_count": prompt_eval_count,
            "eval_count": eval_count,
            "total_tokens": data.get("total_tokens"),
            "input_tokens_per_s": data.get("input_tokens_per_s"),
            "output_tokens_per_s": data.get("output_tokens_per_s"),
            "estimated_cost_usd": estimate_cost(prompt_eval_count, eval_count),
            "confidence": data.get("confidence"),
            "reason": data.get("reason"),
            "raw_llm_response": data.get("raw_llm_response"),
            "error": data.get("error")
        }

    except Exception as exc:
        return {
            "trial_index": index,
            "trial_id": trial_id,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "prompt": prompt,
            "expected_action": expected_action,
            "llm_action": None,
            "is_correct": False,
            "schema_valid": False,
            "mqtt_published": False,
            "architecture_success": False,
            "api_elapsed_ms_client": (time.perf_counter() - start) * 1000,
            "api_elapsed_ms_backend": None,
            "backend_elapsed_ms": None,
            "ollama_elapsed_ms": None,
            "mqtt_publish_ms": None,
            "prompt_eval_count": 0,
            "eval_count": 0,
            "total_tokens": 0,
            "input_tokens_per_s": 0,
            "output_tokens_per_s": 0,
            "estimated_cost_usd": 0,
            "confidence": None,
            "reason": None,
            "raw_llm_response": None,
            "error": str(exc)
        }


def create_supervision_excel(df: pd.DataFrame):
    supervision = df.copy()
    supervision["accion_correcta_supervisor"] = ""
    supervision["evaluacion_supervisor"] = "no evaluado"
    supervision["calidad_1_5"] = ""
    supervision["observaciones_supervisor"] = ""

    supervision.to_excel(XLSX_OUTPUT, index=False)

    wb = load_workbook(XLSX_OUTPUT)
    ws = wb.active
    ws.title = "Supervision"

    header_fill = PatternFill("solid", fgColor="E00034")
    header_font = Font(color="FFFFFF", bold=True)
    thin = Side(border_style="thin", color="CCCCCC")

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = Border(top=thin, bottom=thin, left=thin, right=thin)

    for row in ws.iter_rows(min_row=2):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            cell.border = Border(top=thin, bottom=thin, left=thin, right=thin)

    headers = [cell.value for cell in ws[1]]

    def col_letter(name):
        idx = headers.index(name) + 1
        return ws.cell(row=1, column=idx).column_letter

    action_col = col_letter("accion_correcta_supervisor")
    eval_col = col_letter("evaluacion_supervisor")
    quality_col = col_letter("calidad_1_5")

    action_dv = DataValidation(type="list", formula1='"on,off,none"', allow_blank=True)
    eval_dv = DataValidation(type="list", formula1='"correcto,parcial,incorrecto,no evaluado"', allow_blank=True)
    quality_dv = DataValidation(type="whole", operator="between", formula1="1", formula2="5", allow_blank=True)

    ws.add_data_validation(action_dv)
    ws.add_data_validation(eval_dv)
    ws.add_data_validation(quality_dv)

    action_dv.add(f"{action_col}2:{action_col}{len(supervision)+1}")
    eval_dv.add(f"{eval_col}2:{eval_col}{len(supervision)+1}")
    quality_dv.add(f"{quality_col}2:{quality_col}{len(supervision)+1}")

    for col in ws.columns:
        max_len = 0
        col_letter_value = col[0].column_letter
        for cell in col:
            value = str(cell.value) if cell.value is not None else ""
            max_len = max(max_len, len(value))
        ws.column_dimensions[col_letter_value].width = min(max(max_len + 2, 12), 50)

    ws.freeze_panes = "A2"
    wb.save(XLSX_OUTPUT)


def print_summary(df: pd.DataFrame):
    valid = df.dropna(subset=["llm_action"]).copy()

    print("\n" + "=" * 60)
    print("RESUMEN DEL EXPERIMENTO")
    print("=" * 60)
    print(f"Pruebas totales      : {len(df)}")
    print(f"Accuracy             : {accuracy_score(valid['expected_action'], valid['llm_action']):.4f}")
    print(f"Macro F1             : {f1_score(valid['expected_action'], valid['llm_action'], average='macro'):.4f}")
    print(f"JSON validity rate   : {df['schema_valid'].mean():.4f}")
    print(f"MQTT publish rate    : {df['mqtt_published'].mean():.4f}")
    print(f"Architecture success : {df['architecture_success'].mean():.4f}")
    print(f"Costo estimado (USD) : {df['estimated_cost_usd'].sum():.8f}")
    print("\nReporte de clasificación:")
    print(classification_report(valid["expected_action"], valid["llm_action"]))


def main():
    print(f"Iniciando {N_RUNS} pruebas contra {BACKEND_URL}")
    print("Asegúrate de que el backend esté corriendo: uvicorn main:app --reload --port 8000\n")

    rows = []
    for i in range(1, N_RUNS + 1):
        print(f"  Prueba {i:3d}/{N_RUNS}", end=" ... ")
        row = run_single_test(i)
        status = "✓" if row["is_correct"] else "✗"
        print(f"{status}  [{row['expected_action']} → {row['llm_action']}]  {row.get('api_elapsed_ms_client', 0):.0f} ms")
        rows.append(row)
        time.sleep(0.2)

    df = pd.DataFrame(rows)
    df.to_csv(CSV_OUTPUT, index=False, encoding="utf-8-sig")
    print(f"\nCSV guardado: {CSV_OUTPUT}")

    create_supervision_excel(df)
    print(f"Excel guardado: {XLSX_OUTPUT}")

    print_summary(df)


if __name__ == "__main__":
    main()
