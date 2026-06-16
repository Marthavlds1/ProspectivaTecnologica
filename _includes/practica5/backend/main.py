import os
import time
from typing import Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from openai import OpenAI
from pydantic import BaseModel, Field


load_dotenv()

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"


COPILOT_PROFILES: Dict[str, Dict[str, str]] = {
    "general": {
        "label": "Asistente general",
        "system_prompt": (
            "Eres un asistente general amable, claro y útil. Respondes cualquier pregunta de forma ordenada "
            "y con lenguaje sencillo. Si no sabes algo con certeza, lo dices abiertamente en lugar de inventar."
        ),
    },
    "nutriologo": {
        "label": "Nutriólogo",
        "system_prompt": (
            "Eres un nutriólogo virtual con experiencia en alimentación saludable y balanceada. "
            "Ayudas a calcular porciones, proponer planes de alimentación, explicar el valor nutricional de alimentos "
            "y orientar sobre dietas especiales (vegetariana, sin gluten, baja en sodio, etc.). "
            "Siempre recuerdas que tus recomendaciones son orientativas y que para diagnósticos o condiciones médicas "
            "específicas el usuario debe consultar a un profesional de la salud. "
            "Cuando el usuario mencione ingredientes disponibles, sugiere opciones nutritivas y equilibradas."
        ),
    },
    "compras": {
        "label": "Gestor de compras de alacena",
        "system_prompt": (
            "Eres un asistente especializado en gestión de despensa y listas de compras. "
            "Tu trabajo es ayudar al usuario a saber qué le falta en su alacena, qué está por vencerse, "
            "qué conviene comprar según temporada o precio, y cómo organizar una lista de supermercado eficiente. "
            "Cuando el usuario te diga qué tiene en casa, analiza qué falta para preparar comidas completas. "
            "Sugiere cantidades razonables, marcas genéricas cuando sea posible y agrupa los productos por sección "
            "del supermercado (lácteos, verduras, abarrotes, etc.) para hacer la compra más rápida."
        ),
    },
    "chef": {
        "label": "Chef inventarecetas",
        "system_prompt": (
            "Eres un chef creativo especializado en inventar recetas con lo que el usuario tiene disponible en casa. "
            "Cuando el usuario te diga qué ingredientes tiene, propones una o varias recetas viables, creativas y deliciosas. "
            "Incluyes: nombre de la receta, tiempo de preparación, porciones, lista de ingredientes con cantidades, "
            "pasos detallados y un tip de presentación. "
            "Si faltan ingredientes clave, propones sustitutos con lo que hay disponible. "
            "Adaptas las recetas al nivel de cocina que indique el usuario (principiante, intermedio, avanzado). "
            "Siempre explicas el por qué de las técnicas para que el usuario aprenda mientras cocina."
        ),
    },
}


PROVIDER_MODELS = {
    "ollama": [
        "llama3.2:3b",
        "gemma3:4b",
        "qwen2.5:7b",
        "mistral:7b",
    ],
    "gemini": [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ],
    "groq": [
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant",
    ],
    "openrouter": [
        "meta-llama/llama-3.1-8b-instruct:free",
        "qwen/qwen-2.5-7b-instruct:free",
    ],
}


app = FastAPI(
    title="Chatbot híbrido con Ollama y APIs externas",
    description="API intermedia para comparar LLM local con modelos remotos de Gemini, Groq y OpenRouter.",
    version="3.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    provider: str = Field(default="ollama", min_length=1, max_length=50)
    model: str = Field(default="llama3.2:3b", min_length=1, max_length=150)
    copilot_profile: str = Field(default="generico", min_length=1, max_length=50)
    system_prompt: str = Field(default="", max_length=6000)
    temperature: float = Field(default=0.7, ge=0.0, le=1.2)
    top_p: float = Field(default=0.9, ge=0.1, le=1.0)
    max_tokens: int = Field(default=250, ge=20, le=1000)
    num_ctx: int = Field(default=4096, ge=512, le=8192)
    repeat_penalty: float = Field(default=1.1, ge=1.0, le=2.0)
    keep_alive: str = Field(default="5m", max_length=20)


class ChatMetrics(BaseModel):
    wall_time_s: float
    provider_duration_s: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    tokens_per_second: float
    raw_provider_metrics: Optional[dict] = None


class ChatResponse(BaseModel):
    provider: str
    model: str
    copilot_profile: str
    copilot_label: str
    system_prompt_used: str
    reply: str
    metrics: ChatMetrics


@app.get("/")
def root():
    return {
        "message": "API de chatbot híbrido con Ollama y APIs externas",
        "docs": "/docs",
        "health": "/health",
        "profiles": "/profiles",
        "providers": "/providers",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/profiles")
def profiles():
    return COPILOT_PROFILES


@app.get("/providers")
def providers():
    return PROVIDER_MODELS


def get_profile(profile_id: str) -> Dict[str, str]:
    if profile_id not in COPILOT_PROFILES:
        raise HTTPException(
            status_code=400,
            detail=f"Perfil no válido: {profile_id}. Usa GET /profiles para ver perfiles disponibles.",
        )
    return COPILOT_PROFILES[profile_id]


def validate_provider(provider: str) -> str:
    provider = provider.strip().lower()
    if provider not in PROVIDER_MODELS:
        raise HTTPException(
            status_code=400,
            detail=f"Proveedor no válido: {provider}. Usa GET /providers para ver proveedores disponibles.",
        )
    return provider


def build_messages(system_prompt: str, user_message: str) -> List[Dict[str, str]]:
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]


def call_ollama(request: ChatRequest, messages: List[Dict[str, str]]) -> Tuple[str, ChatMetrics]:
    payload = {
        "model": request.model.strip(),
        "messages": messages,
        "stream": False,
        "keep_alive": request.keep_alive,
        "options": {
            "temperature": request.temperature,
            "top_p": request.top_p,
            "num_predict": request.max_tokens,
            "num_ctx": request.num_ctx,
            "repeat_penalty": request.repeat_penalty,
        },
    }

    start_time = time.perf_counter()
    response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)
    end_time = time.perf_counter()

    response.raise_for_status()
    data = response.json()

    reply = data.get("message", {}).get("content", "")
    total_duration_s = data.get("total_duration", 0) / 1e9
    prompt_tokens = data.get("prompt_eval_count", 0)
    completion_tokens = data.get("eval_count", 0)
    eval_duration_s = data.get("eval_duration", 0) / 1e9
    total_tokens = prompt_tokens + completion_tokens
    tokens_per_second = completion_tokens / eval_duration_s if eval_duration_s > 0 else 0

    return reply, ChatMetrics(
        wall_time_s=end_time - start_time,
        provider_duration_s=total_duration_s,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        tokens_per_second=tokens_per_second,
        raw_provider_metrics={
            "load_duration_s": data.get("load_duration", 0) / 1e9,
            "eval_duration_s": eval_duration_s,
        },
    )


def call_gemini(request: ChatRequest, messages: List[Dict[str, str]]) -> Tuple[str, ChatMetrics]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Falta GEMINI_API_KEY en el archivo .env del backend.")

    client = genai.Client(api_key=api_key)
    system_prompt = messages[0]["content"]
    user_message = messages[1]["content"]
    contents = f"{system_prompt}\n\nUsuario:\n{user_message}"

    start_time = time.perf_counter()
    response = client.models.generate_content(
        model=request.model,
        contents=contents,
        config={
            "temperature": request.temperature,
            "top_p": request.top_p,
            "max_output_tokens": request.max_tokens,
        },
    )
    end_time = time.perf_counter()

    reply = response.text or ""
    usage = getattr(response, "usage_metadata", None)
    prompt_tokens = int(getattr(usage, "prompt_token_count", 0) or 0)
    completion_tokens = int(getattr(usage, "candidates_token_count", 0) or 0)
    total_tokens = int(getattr(usage, "total_token_count", 0) or (prompt_tokens + completion_tokens))
    wall_time_s = end_time - start_time
    tokens_per_second = completion_tokens / wall_time_s if wall_time_s > 0 else 0

    return reply, ChatMetrics(
        wall_time_s=wall_time_s,
        provider_duration_s=wall_time_s,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        tokens_per_second=tokens_per_second,
        raw_provider_metrics={},
    )


def call_openai_compatible(
    request: ChatRequest,
    messages: List[Dict[str, str]],
    api_key_env: str,
    base_url: str,
) -> Tuple[str, ChatMetrics]:
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise HTTPException(status_code=500, detail=f"Falta {api_key_env} en el archivo .env del backend.")

    client = OpenAI(api_key=api_key, base_url=base_url)

    start_time = time.perf_counter()
    response = client.chat.completions.create(
        model=request.model,
        messages=messages,
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens,
    )
    end_time = time.perf_counter()

    reply = response.choices[0].message.content or ""
    usage = response.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    total_tokens = usage.total_tokens if usage else prompt_tokens + completion_tokens
    wall_time_s = end_time - start_time
    tokens_per_second = completion_tokens / wall_time_s if wall_time_s > 0 else 0

    return reply, ChatMetrics(
        wall_time_s=wall_time_s,
        provider_duration_s=wall_time_s,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        tokens_per_second=tokens_per_second,
        raw_provider_metrics={},
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    provider = validate_provider(request.provider)
    profile = get_profile(request.copilot_profile)

    system_prompt_used = request.system_prompt.strip()
    if not system_prompt_used:
        system_prompt_used = profile["system_prompt"]

    messages = build_messages(system_prompt_used, request.message)

    try:
        if provider == "ollama":
            reply, metrics = call_ollama(request, messages)
        elif provider == "gemini":
            reply, metrics = call_gemini(request, messages)
        elif provider == "groq":
            reply, metrics = call_openai_compatible(
                request=request, messages=messages,
                api_key_env="GROQ_API_KEY",
                base_url="https://api.groq.com/openai/v1",
            )
        elif provider == "openrouter":
            reply, metrics = call_openai_compatible(
                request=request, messages=messages,
                api_key_env="OPENROUTER_API_KEY",
                base_url="https://openrouter.ai/api/v1",
            )
        else:
            raise HTTPException(status_code=400, detail="Proveedor no implementado.")

    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Ollama. Verifica que esté ejecutándose.") from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="La solicitud tardó demasiado tiempo.") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(status_code=500, detail=f"Error HTTP del proveedor: {str(exc)}") from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error inesperado al consultar {provider}: {str(exc)}") from exc

    return ChatResponse(
        provider=provider,
        model=request.model,
        copilot_profile=request.copilot_profile,
        copilot_label=profile["label"],
        system_prompt_used=system_prompt_used,
        reply=reply,
        metrics=metrics,
    )