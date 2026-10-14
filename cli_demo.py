#!/usr/bin/env python3
"""
Interaktywna aplikacja konsolowa (CLI) do testowania 2-etapowego pipeline'u
ekstrakcji zapytań modowych (Krok 1: Kategoria -> Krok 2: Cechy Guided Decoding).

Obsługiwane modele:
  [1] Gemini 3.5 Flash-Lite (Google Cloud Vertex AI, multi-region 'eu')
  [2] Gemini 2.5 Flash-Lite (Google Cloud Vertex AI, 'europe-central2' Warszawa)
  [3] Qwen 3.8 27B          (Cerebras WSE-3 via OpenRouter)
  [4] Wszystkie 3 modele    (Tryb porównawczy Side-by-Side)
"""

import os
import sys
import json
import time
import logging
import warnings
import argparse
from typing import Dict, Any, Tuple, Optional

# Wyciszenie komunikatów ostrzeżeń SDK (ADC quota warning / AFC log) dla czystego CLI
warnings.filterwarnings("ignore", category=UserWarning)
logging.getLogger("google_genai").setLevel(logging.ERROR)

# Dodanie ścieżki do katalogu evaluation
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "evaluation"))

from google import genai
from google.genai import types
import httpx

from evaluate_gemini_extraction import (
    ALLOWED_CATEGORIES,
    CategorySelection,
    CATEGORY_MODELS,
    FEW_SHOT_EXAMPLES,
    call_with_retry,
    robust_json_loads,
)

# Kolory ANSI dla czytelnego interfejsu w terminalu
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RED = "\033[91m"
DIM = "\033[2m"
RESET = "\033[0m"


def load_dotenv_if_exists():
    """Wczytuje zmienne z pliku .env (jeśli istnieje w katalogu głównym)."""
    env_path = os.path.join(PROJECT_ROOT, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v


# Konfiguracja dostępnych modeli
MODELS_CONFIG = {
    "1": {
        "key": "3.5",
        "name": "Gemini 3.5 Flash-Lite",
        "provider": "vertex",
        "model_id": "gemini-3.5-flash-lite",
        "location": "eu",
        "desc": "Google Cloud Vertex AI (Multi-region EU)",
    },
    "2": {
        "key": "2.5",
        "name": "Gemini 2.5 Flash-Lite",
        "provider": "vertex",
        "model_id": "gemini-2.5-flash-lite",
        "location": "europe-central2",
        "desc": "Google Cloud Vertex AI (Warszawa - europe-central2)",
    },
    "3": {
        "key": "qwen",
        "name": "Qwen 3.8 27B",
        "provider": "openrouter",
        "model_id": "qwen/qwen3.8-27b",
        "location": "Cerebras WSE-3",
        "desc": "OpenRouter -> Cerebras (Open-Weights)",
    },
    "4": {
        "key": "all",
        "name": "Porównaj wszystkie 3 modele (Side-by-Side)",
        "provider": "all",
        "model_id": "all",
        "location": "EU / Warszawa / Cerebras",
        "desc": "Uruchamia zapytanie kolejno na wszystkich 3 modelach",
    },
}


class FashionPipelineRunner:
    """Zarządza klientami API oraz wykonuje Krok 1 i Krok 2 na wybranym modelu."""

    def __init__(self):
        load_dotenv_if_exists()
        self.project_id = (
            os.environ.get("GOOGLE_CLOUD_PROJECT")
            or os.environ.get("GCP_PROJECT")
            or "project-3a86f100-1aae-4780-84b"
        )
        self._vertex_clients: Dict[str, genai.Client] = {}
        self._openrouter_http: Optional[httpx.Client] = None
        self._openrouter_key: Optional[str] = None

    def get_vertex_client(self, location: str) -> genai.Client:
        if location not in self._vertex_clients:
            if os.environ.get("GEMINI_API_KEY"):
                self._vertex_clients[location] = genai.Client()
            else:
                self._vertex_clients[location] = genai.Client(
                    vertexai=True, project=self.project_id, location=location
                )
        return self._vertex_clients[location]

    def get_openrouter_client(self) -> Tuple[httpx.Client, str]:
        if self._openrouter_http is None or not self._openrouter_key:
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                print(f"{YELLOW}Brak zmiennej środowiskowej OPENROUTER_API_KEY dla modelu Qwen.{RESET}")
                api_key = input("Wklej klucz OPENROUTER_API_KEY (lub naciśnij Enter, aby anulować): ").strip()
                if not api_key:
                    raise ValueError("Klucz OPENROUTER_API_KEY jest wymagany do uruchomienia modelu Qwen 3.8 27B.")
                os.environ["OPENROUTER_API_KEY"] = api_key
            self._openrouter_key = api_key
            self._openrouter_http = httpx.Client(timeout=30.0)
        return self._openrouter_http, self._openrouter_key

    def _call_openrouter_chat(self, model_id: str, messages: list, max_tokens: int) -> str:
        http_client, api_key = self.get_openrouter_client()
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.0,
            "max_tokens": max_tokens,
            "provider": {"order": ["Cerebras"], "allow_fallbacks": False},
            "reasoning": {"effort": "none"},
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        def _do_post():
            resp = http_client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}: {resp.text}")
            data = resp.json()
            return data["choices"][0]["message"]["content"] or "{}"

        return call_with_retry(_do_post)

    # ------------------------------------------------------------------
    # VERTEX AI (GEMINI 3.5 FLASH-LITE / GEMINI 2.5 FLASH-LITE)
    # ------------------------------------------------------------------
    def _run_vertex_step_1(self, client: genai.Client, model_id: str, query: str) -> Tuple[str, float]:
        prompt = f"""You are an expert e-commerce fashion taxonomy classifier.
Classify the user shopping query into EXACTLY ONE of the following fashion categories:
{json.dumps(ALLOWED_CATEGORIES, indent=2)}

Rules:
1. If the query clearly matches one category, return its exact name.
2. If the query is about accessories, undergarments, jewelry, bags, hats, socks, belts, or other non-apparel items, return 'None'.
3. Disambiguation Guide for Borderline Cases:
   - "track jacket" / athletic zip-up -> "Hoodies & Sweatshirts"
   - "polo shirt" / golf polo -> "T-Shirts & Tops"
   - "cardigan" / knit sweater -> "Sweaters & Cardigans"
   - "t-shirt dress" / "shirt dress" -> "Dresses"
   - "windbreaker" / "fleece jacket" -> "Jackets & Coats"
   - "shorts" (e.g. "mens shorts", "denim shorts") -> "Pants & Trousers"
   - "belts", "hats", "socks", "wallets" -> "None"

User Query: "{query}"
"""
        t0 = time.time()
        response = call_with_retry(
            lambda: client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CategorySelection,
                    temperature=0.0,
                ),
            )
        )
        s1_ms = (time.time() - t0) * 1000
        result = robust_json_loads(response.text)
        selected = result.get("category", "None")
        cat = selected if selected in ALLOWED_CATEGORIES else "None"
        return cat, s1_ms

    def _run_vertex_step_2(
        self, client: genai.Client, model_id: str, query: str, category: str
    ) -> Tuple[Dict[str, Any], str, float]:
        model_class = CATEGORY_MODELS[category]
        few_shot = FEW_SHOT_EXAMPLES.get(category)

        few_shot_block = ""
        if few_shot:
            few_shot_block = f"""
Example for this category:
Input Query: "{few_shot['query']}"
Output:
{json.dumps(few_shot['output'], indent=2)}
"""

        prompt = f"""Extract fashion product attributes from the user query into the schema.

Important Rules:
1. Extract attributes that are explicitly stated in the query.
2. CRITICAL: DO NOT guess or infer unmentioned default traits (e.g. do not assume sneakers are flat, do not assume coats are wool or unhooded). If an attribute is not explicitly mentioned, LEAVE IT null.
3. Multi-value & Operator Rules:
   - For styles, fits, cuts, lengths, fastenings, or heel types (e.g. 'midi or maxi', 'straight or wide leg', 'slip-on or lace-up'): return all requested options in the corresponding list.
   - For colors and materials: return all mentioned options in the list.
     * Set operator to 'OR' if the user is open to either alternative (e.g. 'linen or cotton', 'black or navy').
     * Set operator to 'AND' if the single item combines multiple values (e.g. 'black and white', 'cotton polyester blend').
     * If only one color or material is mentioned, leave the operator null.
4. If a brand or company name is present in the query, extract its normalized official name into 'brands' list. If no brand is present, leave 'brands' null.
5. Put any leftover terms (occasions, subjective styles, or unmapped words) into residual_text. Do not put the brand name into residual_text if captured in 'brands'.
{few_shot_block}
User Query: "{query}"
Category: "{category}"
"""
        t0 = time.time()
        response = call_with_retry(
            lambda: client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=model_class,
                    temperature=0.0,
                ),
            )
        )
        s2_ms = (time.time() - t0) * 1000
        result = robust_json_loads(response.text)
        residual = result.pop("residual_text", "")
        extracted_attrs = {k: v for k, v in result.items() if v is not None}
        return extracted_attrs, residual, s2_ms

    # ------------------------------------------------------------------
    # OPENROUTER / CEREBRAS (QWEN 3.8 27B)
    # ------------------------------------------------------------------
    def _run_qwen_step_1(self, model_id: str, query: str) -> Tuple[str, float]:
        system_prompt = f"""You are an expert e-commerce fashion taxonomy classifier.
Classify the user shopping query into EXACTLY ONE of the following fashion categories:
{json.dumps(ALLOWED_CATEGORIES, indent=2)}

Rules:
1. If the query clearly matches one category, return its exact name.
2. If the query is about accessories, undergarments, jewelry, bags, hats, socks, belts, or other non-apparel items, return 'None'.
3. Disambiguation Guide for Borderline Cases:
   - "track jacket" / athletic zip-up -> "Hoodies & Sweatshirts"
   - "polo shirt" / golf polo -> "T-Shirts & Tops"
   - "cardigan" / knit sweater -> "Sweaters & Cardigans"
   - "t-shirt dress" / "shirt dress" -> "Dresses"
   - "windbreaker" / "fleece jacket" -> "Jackets & Coats"
   - "shorts" (e.g. "mens shorts", "denim shorts") -> "Pants & Trousers"
   - "belts", "hats", "socks", "wallets" -> "None"

Return strictly valid JSON format: {{"category": "<one of allowed categories or None>"}}
"""
        t0 = time.time()
        raw = self._call_openrouter_chat(
            model_id=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'User Query: "{query}"'},
            ],
            max_tokens=100,
        )
        s1_ms = (time.time() - t0) * 1000
        parsed = robust_json_loads(raw)
        cat = parsed.get("category", "None")
        return (cat if cat in ALLOWED_CATEGORIES else "None"), s1_ms

    def _run_qwen_step_2(
        self, model_id: str, query: str, category: str
    ) -> Tuple[Dict[str, Any], str, float]:
        model_class = CATEGORY_MODELS[category]
        few_shot = FEW_SHOT_EXAMPLES.get(category)
        schema_json = json.dumps(model_class.model_json_schema(), indent=2)

        few_shot_block = ""
        if few_shot:
            few_shot_block = f"""
Example for this category:
Input Query: "{few_shot['query']}"
Output:
{json.dumps(few_shot['output'], indent=2)}
"""
        system_prompt = f"""You are an expert fashion attribute extractor.
Extract fashion product attributes for category "{category}" into the following JSON schema:
{schema_json}

Important Rules:
1. Extract attributes that are explicitly stated in the query.
2. CRITICAL: DO NOT guess or infer unmentioned default traits. If not explicitly mentioned, LEAVE IT null.
3. Multi-value & Operator Rules:
   - For styles, fits, cuts, lengths, fastenings, or heel types: return all requested options in the list.
   - For colors and materials: return all mentioned options in the list.
     * Set operator to 'OR' if alternative.
     * Set operator to 'AND' if combined multi-color/material.
     * Leave operator null if single option.
4. If a brand name is present, extract normalized official name into 'brands' list.
5. Put any leftover terms into residual_text.
{few_shot_block}
Return strictly valid JSON matching the schema.
"""
        t0 = time.time()
        raw = self._call_openrouter_chat(
            model_id=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'User Query: "{query}"'},
            ],
            max_tokens=600,
        )
        s2_ms = (time.time() - t0) * 1000
        parsed = robust_json_loads(raw)
        residual = parsed.pop("residual_text", "")
        extracted_attrs = {k: v for k, v in parsed.items() if v is not None}
        return extracted_attrs, residual, s2_ms

    # ------------------------------------------------------------------
    # WSPÓLNY PUNKT URUCHOMIENIA PIPELINE'U
    # ------------------------------------------------------------------
    def run_pipeline(self, choice_id: str, query: str) -> Dict[str, Any]:
        cfg = MODELS_CONFIG[choice_id]
        provider = cfg["provider"]
        model_id = cfg["model_id"]
        location = cfg["location"]

        if provider == "vertex":
            client = self.get_vertex_client(location)
            cat, s1_ms = self._run_vertex_step_1(client, model_id, query)
            attrs, residual, s2_ms = ({}, "", 0.0)
            if cat != "None":
                attrs, residual, s2_ms = self._run_vertex_step_2(client, model_id, query, cat)
        elif provider == "openrouter":
            cat, s1_ms = self._run_qwen_step_1(model_id, query)
            attrs, residual, s2_ms = ({}, "", 0.0)
            if cat != "None":
                attrs, residual, s2_ms = self._run_qwen_step_2(model_id, query, cat)
        else:
            raise ValueError(f"Nieznany provider: {provider}")

        total_ms = s1_ms + s2_ms
        return {
            "model_name": cfg["name"],
            "model_id": model_id,
            "location": location,
            "query": query,
            "category": cat,
            "attributes": attrs,
            "residual_text": residual,
            "s1_ms": round(s1_ms, 1),
            "s2_ms": round(s2_ms, 1),
            "total_ms": round(total_ms, 1),
        }


def print_single_result(res: Dict[str, Any]):
    """Formatuje i wyświetla wynik pojedynczego modelu w konsoli."""
    print(f"\n{CYAN}{'─' * 80}{RESET}")
    print(f"{BOLD}Model:{RESET}     {GREEN}{res['model_name']}{RESET} {DIM}({res['model_id']} @ {res['location']}){RESET}")
    print(f"{BOLD}Zapytanie:{RESET} \"{YELLOW}{res['query']}{RESET}\"")
    print(f"{CYAN}{'─' * 80}{RESET}")

    # Krok 1
    cat_color = GREEN if res["category"] != "None" else RED
    print(f"{BOLD}[Krok 1] Kategoria:{RESET} {cat_color}{BOLD}{res['category']}{RESET} {DIM}({res['s1_ms']:.0f} ms){RESET}")

    # Krok 2
    if res["category"] == "None":
        print(f"{DIM}[Krok 2] Pominięty (zapytanie spoza 8 kategorii odzieżowych / Out-of-Scope){RESET}")
    else:
        print(f"{BOLD}[Krok 2] Wyciągnięte atrybuty:{RESET} {DIM}({res['s2_ms']:.0f} ms){RESET}")
        attrs = res["attributes"]
        if not attrs:
            print(f"   {DIM}(Brak specyficznych atrybutów z zamkniętej taksonomii){RESET}")
        else:
            for k, v in attrs.items():
                val_str = json.dumps(v, ensure_ascii=False) if isinstance(v, list) else str(v)
                print(f"   • {MAGENTA}{k:20s}{RESET} : {BOLD}{val_str}{RESET}")

        res_txt = res["residual_text"]
        res_display = f'"{res_txt}"' if res_txt else f"{DIM}(puste){RESET}"
        print(f"   • {CYAN}{'residual_text':20s}{RESET} : {res_display}")

    print(f"{CYAN}{'─' * 80}{RESET}")
    print(
        f"{BOLD}Czas całkowity:{RESET} {BOLD}{res['total_ms']:.0f} ms{RESET} ({res['total_ms']/1000:.2f} s) "
        f"{DIM}[K1: {res['s1_ms']:.0f} ms | K2: {res['s2_ms']:.0f} ms]{RESET}"
    )

    # Pełny obiekt JSON
    json_payload = {
        "category": res["category"],
        "extracted_attributes": res["attributes"],
        "residual_text": res["residual_text"],
    }
    print(f"\n{DIM}Wygenerowany JSON (payload dla silnika wyszukiwarki):{RESET}")
    print(json.dumps(json_payload, indent=2, ensure_ascii=False))
    print(f"{CYAN}{'─' * 80}{RESET}\n")


def print_taxonomy_overview():
    """Wyświetla podgląd wszystkich 8 kategorii i przypisanych im atrybutów."""
    print(f"\n{CYAN}{'═' * 80}{RESET}")
    print(f"{BOLD}DOSTĘPNE KATEGORIE I CECHY W TAKSONOMII (GUIDED DECODING){RESET}")
    print(f"{CYAN}{'═' * 80}{RESET}")
    base_fields = [
        "department_gender",
        "colors",
        "color_operator",
        "pattern",
        "materials",
        "material_operator",
        "brands",
        "residual_text",
    ]
    print(f"{BOLD}Cechy wspólne (dla każdej kategorii):{RESET} {', '.join(base_fields)}\n")
    for cat in ALLOWED_CATEGORIES:
        model_cls = CATEGORY_MODELS[cat]
        specific_fields = [k for k in model_cls.model_fields.keys() if k not in base_fields]
        print(f" • {GREEN}{cat:24s}{RESET} -> {', '.join(specific_fields)}")
    print(f"{CYAN}{'═' * 80}{RESET}\n")


def select_model_menu(current_choice: str = "1") -> str:
    print(f"\n{BOLD}Wybierz model do filtrowania zapytań:{RESET}")
    for cid, cfg in MODELS_CONFIG.items():
        marker = f"{GREEN}*{RESET}" if cid == current_choice else " "
        print(f"  {marker} [{BOLD}{cid}{RESET}] {BOLD}{cfg['name']:42s}{RESET} {DIM}— {cfg['desc']}{RESET}")
    choice = input(f"\nTwój wybór [1-4, domyślnie {current_choice}]: ").strip()
    if choice in MODELS_CONFIG:
        return choice
    return current_choice


def interactive_loop(runner: FashionPipelineRunner, initial_choice: str = "1"):
    current_choice = initial_choice
    print(f"{CYAN}{'═' * 80}{RESET}")
    print(f"{BOLD} INTERAKTYWNY TESTER FILTROWANIA ZAPYTAŃ MODOWYCH (2-STAGE PIPELINE){RESET}")
    print(f"{CYAN}{'═' * 80}{RESET}")

    current_choice = select_model_menu(current_choice)

    while True:
        cfg = MODELS_CONFIG[current_choice]
        print(
            f"{DIM}Aktywny model:{RESET} {GREEN}{BOLD}{cfg['name']}{RESET} "
            f"{DIM}| Komendy: [m] zmiana modelu, [s] podgląd cech, [q] wyjście{RESET}"
        )
        try:
            user_input = input(f"{BOLD}Wpisz zapytanie usera > {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nDo zobaczenia!")
            break

        if not user_input:
            continue

        cmd = user_input.lower()
        if cmd in ("q", "quit", "exit", ":q"):
            print("Zamykanie aplikacji.")
            break
        elif cmd in ("m", "/model", "model"):
            current_choice = select_model_menu(current_choice)
            continue
        elif cmd in (":1", ":2", ":3", ":4"):
            current_choice = cmd[1]
            continue
        elif cmd in ("s", "/schema", "schema", "cechy"):
            print_taxonomy_overview()
            continue

        # Wykonanie zapytania
        if current_choice == "4":
            for sub_id in ("1", "2", "3"):
                sub_cfg = MODELS_CONFIG[sub_id]
                print(f"{DIM}Uruchamianie: {sub_cfg['name']}...{RESET}", end="\r", flush=True)
                try:
                    res = runner.run_pipeline(sub_id, user_input)
                    print_single_result(res)
                except Exception as e:
                    print(f"\n{RED}Błąd dla modelu {sub_cfg['name']}: {e}{RESET}\n")
        else:
            print(f"{DIM}Przetwarzanie zapytania ({cfg['name']})...{RESET}", end="\r", flush=True)
            try:
                res = runner.run_pipeline(current_choice, user_input)
                print_single_result(res)
            except Exception as e:
                print(f"\n{RED}Błąd wykonania: {e}{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Konsolowa aplikacja do testowania ekstrakcji cech i kategorii z zapytań modowych."
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="1",
        help="Wybór modelu: '1'/'3.5' (Gemini 3.5), '2'/'2.5' (Gemini 2.5), '3'/'qwen' (Qwen 3.8 27B), '4'/'all' (Wszystkie)",
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Opcjonalne zapytanie bezpośrednio z linii komend (jeśli brak, uruchamia tryb interaktywny).",
    )
    args = parser.parse_args()

    # Mapowanie nazwy modelu na ID wyboru
    model_map = {
        "1": "1",
        "3.5": "1",
        "gemini-3.5": "1",
        "gemini-3.5-flash-lite": "1",
        "2": "2",
        "2.5": "2",
        "gemini-2.5": "2",
        "gemini-2.5-flash-lite": "2",
        "3": "3",
        "qwen": "3",
        "qwen3.8": "3",
        "4": "4",
        "all": "4",
    }
    choice_id = model_map.get(args.model.lower(), "1")
    runner = FashionPipelineRunner()

    if args.query:
        query_str = " ".join(args.query)
        if choice_id == "4":
            for sub_id in ("1", "2", "3"):
                try:
                    res = runner.run_pipeline(sub_id, query_str)
                    print_single_result(res)
                except Exception as e:
                    print(f"{RED}Błąd dla modelu {MODELS_CONFIG[sub_id]['name']}: {e}{RESET}")
        else:
            res = runner.run_pipeline(choice_id, query_str)
            print_single_result(res)
    else:
        interactive_loop(runner, initial_choice=choice_id)


if __name__ == "__main__":
    main()
