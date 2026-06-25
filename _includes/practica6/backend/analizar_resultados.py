from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)


CSV_INPUT = "resultados_llm_led_raw.csv"
OUT_DIR = Path("graficas_resultados")
OUT_DIR.mkdir(exist_ok=True)

LABELS = ["on", "off", "none"]


def load_data():
    df = pd.read_csv(CSV_INPUT)
    return df


def clean_boolean_columns(df):
    bool_columns = ["is_correct", "schema_valid", "mqtt_published", "architecture_success"]
    for col in bool_columns:
        if col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].astype(str).str.lower().map(
                    {"true": True, "false": False, "1": True, "0": False}
                )
            df[col] = df[col].fillna(False).astype(bool)
    return df


def save_metrics_summary(df):
    valid = df.dropna(subset=["llm_action"]).copy()

    if len(valid) == 0:
        raise ValueError("No hay predicciones válidas en llm_action. Revisa si el backend respondió.")

    summary = {
        "n_total": len(df),
        "n_valid_predictions": len(valid),
        "accuracy": accuracy_score(valid["expected_action"], valid["llm_action"]),
        "precision_macro": precision_score(valid["expected_action"], valid["llm_action"], average="macro", zero_division=0),
        "recall_macro": recall_score(valid["expected_action"], valid["llm_action"], average="macro", zero_division=0),
        "f1_macro": f1_score(valid["expected_action"], valid["llm_action"], average="macro", zero_division=0),
        "json_validity_rate": df["schema_valid"].mean(),
        "mqtt_publish_rate": df["mqtt_published"].mean(),
        "architecture_success_rate": df["architecture_success"].mean(),
        "latency_mean_ms": df["api_elapsed_ms_client"].mean(),
        "latency_p50_ms": df["api_elapsed_ms_client"].quantile(0.50),
        "latency_p95_ms": df["api_elapsed_ms_client"].quantile(0.95),
        "latency_p99_ms": df["api_elapsed_ms_client"].quantile(0.99),
        "input_tokens_mean": df["prompt_eval_count"].mean(),
        "output_tokens_mean": df["eval_count"].mean(),
        "total_tokens_mean": df["total_tokens"].mean(),
        "estimated_cost_usd_total": df["estimated_cost_usd"].sum(),
    }

    pd.DataFrame([summary]).to_csv("resumen_metricas.csv", index=False, encoding="utf-8-sig")

    report = classification_report(
        valid["expected_action"], valid["llm_action"],
        labels=LABELS, output_dict=True, zero_division=0
    )
    pd.DataFrame(report).transpose().to_csv("classification_report.csv", encoding="utf-8-sig")

    return pd.DataFrame([summary])


def plot_confusion_matrix(df):
    valid = df.dropna(subset=["llm_action"]).copy()
    cm = confusion_matrix(valid["expected_action"], valid["llm_action"], labels=LABELS)

    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=LABELS)
    disp.plot(ax=ax, values_format="d", colorbar=False)
    ax.set_title("Matriz de confusión: intención LED")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "confusion_matrix.png", dpi=180)
    plt.close(fig)
    print(f"  Guardada: {OUT_DIR / 'confusion_matrix.png'}")


def plot_latency_by_trial(df):
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(df["trial_index"], df["api_elapsed_ms_client"], marker="o", linewidth=1.3, markersize=4, label="Latencia total cliente")
    ax.plot(df["trial_index"], df["ollama_elapsed_ms"], marker="o", linewidth=1.3, markersize=4, label="Latencia Ollama")
    ax.set_title("Latencia por iteración")
    ax.set_xlabel("Iteración")
    ax.set_ylabel("Tiempo (ms)")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT_DIR / "latency_by_trial.png", dpi=180)
    plt.close(fig)
    print(f"  Guardada: {OUT_DIR / 'latency_by_trial.png'}")


def plot_latency_boxplot(df):
    data = [
        df["api_elapsed_ms_client"].dropna(),
        df["ollama_elapsed_ms"].dropna(),
        df["mqtt_publish_ms"].dropna(),
    ]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.boxplot(data, tick_labels=["Total cliente", "Ollama", "MQTT"], showmeans=True)
    ax.set_title("Distribución de latencia")
    ax.set_ylabel("Tiempo (ms)")
    ax.grid(True, axis="y")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "latency_boxplot.png", dpi=180)
    plt.close(fig)
    print(f"  Guardada: {OUT_DIR / 'latency_boxplot.png'}")


def plot_tokens_vs_latency(df):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(df["total_tokens"], df["api_elapsed_ms_client"], alpha=0.75)
    ax.set_title("Tokens totales vs latencia")
    ax.set_xlabel("Tokens totales")
    ax.set_ylabel("Latencia total cliente (ms)")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "tokens_vs_latency.png", dpi=180)
    plt.close(fig)
    print(f"  Guardada: {OUT_DIR / 'tokens_vs_latency.png'}")


def plot_success_rates(df):
    metrics = {
        "JSON válido": df["schema_valid"].mean(),
        "MQTT publicado": df["mqtt_published"].mean(),
        "Éxito arquitectura": df["architecture_success"].mean(),
        "Clasificación correcta": df["is_correct"].mean(),
    }
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(metrics.keys(), metrics.values(), color=["#2563eb", "#16a34a", "#9333ea", "#E00034"])
    ax.set_title("Tasas de éxito del experimento")
    ax.set_ylabel("Tasa (0 a 1)")
    ax.set_ylim(0, 1.1)
    ax.grid(True, axis="y")
    for bar, value in zip(bars, metrics.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.2f}", ha="center", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_DIR / "success_rates.png", dpi=180)
    plt.close(fig)
    print(f"  Guardada: {OUT_DIR / 'success_rates.png'}")


def main():
    print(f"Leyendo: {CSV_INPUT}")
    df = load_data()
    df = clean_boolean_columns(df)

    print("\nCalculando métricas...")
    summary = save_metrics_summary(df)
    print("  Guardado: resumen_metricas.csv")
    print("  Guardado: classification_report.csv")

    print("\nGenerando gráficas...")
    plot_confusion_matrix(df)
    plot_latency_by_trial(df)
    plot_latency_boxplot(df)
    plot_tokens_vs_latency(df)
    plot_success_rates(df)

    print("\n" + "=" * 60)
    print("RESUMEN DE MÉTRICAS")
    print("=" * 60)
    for col in summary.columns:
        print(f"  {col:<35} {summary[col].values[0]}")


if __name__ == "__main__":
    main()
