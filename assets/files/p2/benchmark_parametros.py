import csv, time, requests
from datetime import datetime

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:3b"
N_CYCLES = 5
OUTPUT_CSV = "benchmark_parametros.csv"

PROMPT = (
    "Eres el asistente de una alacena inteligente. "
    "El usuario tiene: tomates, cebolla, ajo, pasta y queso. "
    "Sugiere una receta sencilla con esos ingredientes en máximo 100 palabras."
)

EXPERIMENTS = [
    {"param": "temperature", "value": 0.0,  "label": "temperature_0.0"},
    {"param": "temperature", "value": 0.7,  "label": "temperature_0.7"},
    {"param": "temperature", "value": 1.1,  "label": "temperature_1.1"},
    {"param": "top_p",       "value": 0.7,  "label": "top_p_0.7"},
    {"param": "top_p",       "value": 0.9,  "label": "top_p_0.9"},
    {"param": "top_p",       "value": 0.95, "label": "top_p_0.95"},
    {"param": "repeat_penalty", "value": 1.0, "label": "repeat_penalty_1.0"},
    {"param": "repeat_penalty", "value": 1.2, "label": "repeat_penalty_1.2"},
    {"param": "repeat_penalty", "value": 1.5, "label": "repeat_penalty_1.5"},
]

BASE_OPTIONS = {
    "temperature": 0.7, "top_p": 0.9, "top_k": 40,
    "min_p": 0.0, "num_ctx": 2048, "num_predict": 140,
    "repeat_penalty": 1.1,
}

def evaluate_quality(text):
    if not text or len(text.strip()) < 20:
        return 0
    score = 0
    keywords = ["receta","pasta","tomate","ingrediente","mezcla","cocina","minuto","agua","sal"]
    if 100 <= len(text) <= 700: score += 2
    score += min(sum(1 for w in keywords if w in text.lower()), 4)
    words = text.split()
    if len(set(words)) / max(len(words),1) > 0.45: score += 2
    if len(text) > 80: score += 2
    return min(score, 10)

fieldnames = [
    "timestamp","model","experiment_label","param_name","param_value",
    "cycle","temperature","top_p","repeat_penalty",
    "total_duration_s","wall_time_s","prompt_eval_count","eval_count",
    "tokens_per_second","response_chars","quality_score","notes",
]

print("="*60)
print(f"PARTE C — VARIACION DE PARAMETROS")
print(f"Modelo: {MODEL} | Ciclos: {N_CYCLES} | Total: {len(EXPERIMENTS)*N_CYCLES}")
print("="*60)

with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for exp in EXPERIMENTS:
        options = BASE_OPTIONS.copy()
        options[exp["param"]] = exp["value"]
        print(f"\n>>> {exp['label']}")

        for cycle in range(1, N_CYCLES + 1):
            print(f"  Ciclo {cycle}/{N_CYCLES}")
            row = {
                "timestamp": datetime.now().isoformat(),
                "model": MODEL,
                "experiment_label": exp["label"],
                "param_name": exp["param"],
                "param_value": exp["value"],
                "cycle": cycle,
                "temperature": options["temperature"],
                "top_p": options["top_p"],
                "repeat_penalty": options["repeat_penalty"],
                "total_duration_s":"","wall_time_s":"","prompt_eval_count":"",
                "eval_count":"","tokens_per_second":"","response_chars":"",
                "quality_score":"","notes":"",
            }
            try:
                payload = {"model":MODEL,"prompt":PROMPT,"stream":False,"keep_alive":"30m","options":options}
                start = time.perf_counter()
                r = requests.post(OLLAMA_URL, json=payload, timeout=300)
                wall = time.perf_counter() - start
                r.raise_for_status()
                d = r.json()
                ed = d.get("eval_duration",0)/1e9
                ec = d.get("eval_count",0)
                text = d.get("response","")
                row.update({
                    "total_duration_s": round(d.get("total_duration",0)/1e9, 3),
                    "wall_time_s": round(wall, 3),
                    "prompt_eval_count": d.get("prompt_eval_count",0),
                    "eval_count": ec,
                    "tokens_per_second": round(ec/ed if ed>0 else 0, 3),
                    "response_chars": len(text),
                    "quality_score": evaluate_quality(text),
                })
                print(f"    OK | {row['total_duration_s']}s | {row['tokens_per_second']} tok/s")
            except Exception as e:
                row["notes"] = str(e)
                print(f"    ERROR: {e}")
            writer.writerow(row)

print(f"\n{'='*60}")
print(f"Listo. CSV guardado: {OUTPUT_CSV}")
print(f"{'='*60}")