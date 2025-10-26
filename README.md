# 🎙️ Wise Knowledge - Podcast Transcripts Vector Search

Inteligentna baza wiedzy z transkryptami podcastów wykorzystująca semantic search w Qdrant. System przetwarza transkrypcje podcastów i umożliwia semantyczne wyszukiwanie treści za pomocą embeddingów OpenAI.

## 🎯 Czym jest ten projekt?

Kompletny system RAG (Retrieval-Augmented Generation) składający się z:
1. **Pipeline przetwarzania** - transformacja transkryptów JSON → embeddingi → baza wektorowa
2. **MCP Server** - API zgodne z Model Context Protocol do wyszukiwania semantycznego
3. **RAG Client** - interaktywny chat z Ollama wykorzystujący bazę wiedzy
4. **Claude Skill** - bezpośrednia integracja z Claude Code

Projekt można używać samodzielnie (RAG client) lub jako backend wiedzy dla AI assistants (Claude, własne agenty).

## 📋 Opis projektu

System umożliwiający budowę prywatnej bazy wiedzy z transkryptów podcastów z wykorzystaniem wyszukiwania semantycznego. Projekt wykorzystuje:
- **Qdrant** - bazę wektorową do przechowywania embeddingów
- **OpenAI Embeddings** (text-embedding-3-small) - do generowania reprezentacji wektorowych 512-wymiarowych
- **Python + uv** - do zarządzania zależnościami i uruchamiania skryptów
- **Docker** - do lokalnego uruchomienia Qdrant

## ✨ Funkcjonalności

- 🔍 **Semantic Search** - wyszukiwanie podobieństw semantycznych, nie tylko słów kluczowych
- 📊 **Strukturyzowane metadane** - integracja danych JSON z informacjami o epizodach, sekcjach, key points, tagach
- 🎯 **Inteligentny chunking** - jedna sekcja transkryptu = jeden chunk z embeddingiem
- 🏷️ **Zaawansowane metadane** - episode_id, title, heading, key_points, tags, source_file
- ⚡ **Szybkie wyszukiwanie** - milisekundowe odpowiedzi dzięki indeksom wektorowym Qdrant
- 📝 **Pełny kontekst** - każdy chunk zawiera treść sekcji oraz wszystkie metadane
- 🤖 **MCP Server** - API wyszukiwania przez Model Context Protocol
- 💬 **RAG Chat** - Interaktywny klient z Ollama do rozmów opartych na bazie wiedzy
- 🎨 **Claude Code Skill** - Bezpośrednia integracja z Claude do wyszukiwania w rozmowach

## 🏗️ Architektura

Projekt składa się z czterech głównych komponentów:

```
┌─────────────────────┐
│  transcripts/       │
│  *.json files       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────────┐
│  Ingestion Pipeline │────▶│  Qdrant Database    │
│  (wise_knowledge/)  │     │  - 512-dim vectors  │
│  - Load JSONs       │     │  - Cosine distance  │
│  - OpenAI Embeddings│     │  - Metadata         │
└─────────────────────┘     └──────────┬──────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    ▼                  ▼                  ▼
         ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐
         │   MCP Server     │  │  MCP Client  │  │ Claude Skill │
         │  (mcp_server/)   │  │ (mcp_client/)│  │   (skills/)  │
         │  - Search API    │  │  - Ollama    │  │  - Claude    │
         │  - MCP Protocol  │  │  - RAG Chat  │  │    Code      │
         └──────────────────┘  └──────────────┘  └──────────────┘
```

**Komponenty:**
1. **Ingestion Pipeline** - Przetwarza transkrypty i tworzy embeddingi
2. **Qdrant Database** - Przechowuje wektory i metadane
3. **MCP Server** - Udostępnia API wyszukiwania przez Model Context Protocol
4. **MCP Client** - Interaktywny klient czatu z Ollama (RAG)
5. **Claude Skill** - Integracja z Claude Code do wyszukiwania w rozmowach

## 🚀 Quick Start

### Wymagania

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key
- `uv` (dependency manager)
- Ollama (opcjonalnie, dla MCP Client)

### Instalacja

1. **Sklonuj repozytorium**
```bash
git clone <repo-url>
cd wise_knowledge
```

2. **Uruchom Qdrant**
```bash
cd docker
docker compose up -d
```

Qdrant będzie dostępny pod:
- HTTP API: http://localhost:6333
- gRPC API: http://localhost:6334
- Dashboard: http://localhost:6333/dashboard

3. **Zainstaluj zależności**
```bash
cd wise_knowledge
uv sync
```

4. **Skonfiguruj zmienne środowiskowe**
```bash
cp .env.example .env
# Edytuj .env i dodaj swój OPENAI_API_KEY
```

5. **Uruchom ingestion**
```bash
uv run python main.py
```

Skrypt automatycznie:
- Wczyta wszystkie JSONy z `transcripts/`
- Wygeneruje embeddingi dla każdej sekcji
- Utworzy kolekcję `podcasts_transcripts` w Qdrant (jeśli nie istnieje)
- Zapisze wektory wraz z metadanymi

## 📁 Struktura projektu

```
.
├── docker/
│   └── compose.yaml           # Konfiguracja Qdrant
├── transcripts/               # Pliki JSON z transkryptami
│   ├── strategia_biznesu.json
│   └── ...
├── skills/                    # Claude Code skills
│   └── wise-knowledge-search/ # Skill wyszukiwania
│       ├── SKILL.md           # Definicja skill
│       ├── README.md          # Dokumentacja
│       └── EXAMPLES.md        # Przykłady użycia
├── mcp_server/                # MCP Server (Semantic Search API)
│   ├── tests/                 # Testy MCP server
│   │   ├── conftest.py
│   │   └── test_search.py
│   ├── pyproject.toml         # Zależności MCP server
│   ├── .env.example           # Szablon zmiennych
│   ├── search.py              # Logika wyszukiwania
│   └── main.py                # Implementacja MCP server
├── mcp_client/                # Interaktywny klient z Ollama
│   ├── pyproject.toml         # Zależności klienta
│   ├── .env.example           # Konfiguracja Ollama
│   └── main.py                # Interfejs chat
└── wise_knowledge/            # Pakiet ingestion
    ├── tests/                 # Testy jednostkowe
    │   ├── conftest.py        # Pytest fixtures
    │   └── test_ingest_transcripts.py
    ├── pyproject.toml         # Zależności (uv)
    ├── pytest.ini             # Konfiguracja pytest
    ├── .env.example           # Szablon zmiennych środowiskowych
    ├── main.py                # Entry point aplikacji
    ├── ingest_transcripts.py  # Logika ingestion
    └── explore_database.ipynb # Jupyter notebook do eksploracji danych
```

## 📄 Format JSON transkryptów

Każdy plik JSON w folderze `transcripts/` powinien mieć strukturę:

```json
{
  "episode_id": "ep_001",
  "title": "Tytuł odcinka",
  "summary": "Krótkie podsumowanie całego odcinka",
  "tags": ["tag1", "tag2", "tag3"],
  "sections": [
    {
      "heading": "Nagłówek sekcji",
      "content": "Pełna treść sekcji (użyta do embeddingu)",
      "key_points": [
        "Kluczowy punkt 1",
        "Kluczowy punkt 2"
      ]
    }
  ]
}
```

## 🔧 Konfiguracja

Zmienne środowiskowe w `.env`:

```bash
# Wymagane
OPENAI_API_KEY=sk-...

# Opcjonalne (z wartościami domyślnymi)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                      # Puste dla lokalnej instancji
QDRANT_COLLECTION=podcasts_transcripts
EMBEDDING_MODEL=text-embedding-3-small
EMBED_DIM=512
BATCH_SIZE=64
TRANSCRIPTS_DIR=../transcripts
```

## 🧪 Testing

Projekt używa pytest do testów jednostkowych.

### Uruchomienie testów

```bash
# Zainstaluj dev dependencies
cd wise_knowledge
uv sync --extra dev

# Uruchom wszystkie testy
uv run pytest

# Uruchom testy z coverage report
uv run pytest --cov

# Uruchom konkretny plik testowy
uv run pytest tests/test_ingest_transcripts.py

# Uruchom testy w trybie verbose
uv run pytest -v

# Generuj HTML coverage report
uv run pytest --cov --cov-report=html
# Raport w: htmlcov/index.html
```

### Struktura testów

- `tests/test_ingest_transcripts.py` - testy dla funkcji ingestion
- `tests/conftest.py` - wspólne fixtures dla testów
- `pytest.ini` - konfiguracja pytest

Testy pokrywają:
- Tworzenie kolekcji Qdrant
- Generowanie embeddingów
- Ładowanie i parsowanie JSONów
- Upload do Qdrant
- Obsługę błędów

## 📊 Eksploracja Danych

Projekt zawiera Jupyter notebook do analizy zawartości bazy danych.

### Uruchomienie notebooka

```bash
# Zainstaluj Jupyter i zależności
cd wise_knowledge
uv sync --extra dev

# Uruchom Jupyter Lab
uv run jupyter lab

# Lub Jupyter Notebook
uv run jupyter notebook
```

Następnie otwórz plik [explore_database.ipynb](wise_knowledge/explore_database.ipynb).

### Funkcjonalności notebooka

- ✅ Podgląd informacji o kolekcji Qdrant
- ✅ Wyświetlanie pierwszych punktów z metadanymi
- ✅ Statystyki (liczba epizodów, średnia długość contentu, etc.)
- ✅ Analiza podziału na epizody
- ✅ Wizualizacje (rozkład długości, key points, sekcje na epizod)
- ✅ Wyszukiwanie po metadanych
- ✅ Podgląd szczegółów konkretnego punktu
- ✅ Eksport danych do CSV

## 🔍 Wyszukiwanie Semantyczne

System udostępnia trzy sposoby wyszukiwania w bazie wiedzy:

### 1. MCP Server (API)

Model Context Protocol server udostępniający API wyszukiwania.

**Setup:**
```bash
cd mcp_server
uv sync
cp .env.example .env
# Edytuj .env i dodaj OPENAI_API_KEY

# Uruchom server
uv run python main.py
```

**Integracja z Claude Desktop/Code:**

Dodaj do konfiguracji MCP (np. `~/.config/claude-code/mcp.json`):
```json
{
  "mcpServers": {
    "wise-knowledge": {
      "command": "uv",
      "args": [
        "--directory",
        "/pełna/ścieżka/do/wise_knowledge/mcp_server",
        "run",
        "python",
        "main.py"
      ]
    }
  }
}
```

**Dostępne narzędzia MCP:**
- `search_podcasts` - wyszukiwanie semantyczne z parametrami query, limit, score_threshold
- `get_collection_status` - statystyki bazy wiedzy

**Testy:**
```bash
cd mcp_server
uv sync --extra dev
uv run pytest
uv run pytest --cov  # z coverage
```

### 2. MCP Client (Interaktywny Chat z Ollama)

Konsolowy klient łączący MCP server z lokalnym LLM (Ollama) do rozmów RAG.

**Setup:**
```bash
cd mcp_client
uv sync
cp .env.example .env
# Edytuj .env i ustaw OLLAMA_MODEL (domyślnie: llama3.2:latest)
```

**Wymagania:**
- Ollama zainstalowany i uruchomiony (`ollama serve`)
- Model pobrany (`ollama pull llama3.2:latest`)
- MCP server skonfigurowany (używa `mcp_server/` z projektu)

**Uruchomienie:**
```bash
cd mcp_client
uv run python main.py
```

**Funkcje:**
- Interaktywny chat z pytaniami w naturalnym języku
- RAG workflow: wyszukiwanie → kontekst → Ollama → odpowiedź
- Komenda `status` - statystyki kolekcji
- Opcja wyświetlania szczegółowych wyników wyszukiwania

### 3. Claude Code Skill

Skill dla Claude Code umożliwiający wyszukiwanie bezpośrednio w rozmowach z Claude.

**Instalacja:**
```bash
# macOS
cp -r skills/wise-knowledge-search ~/Library/Application\ Support/Claude/skills/

# Linux
cp -r skills/wise-knowledge-search ~/.config/claude/skills/
```

**Wymagania:**
- Qdrant uruchomiony: `cd docker && docker compose up -d`
- Baza zasilona: `cd wise_knowledge && uv run python main.py`
- MCP server skonfigurowany w Claude Code (patrz wyżej)
- Environment: `mcp_server/.env` z `OPENAI_API_KEY`

**Użycie:**

Claude automatycznie aktywuje skill gdy zapytasz o treści podcastów:
- "Co mówiono w podcastach o strategii marketingowej?"
- "Znajdź odcinki o AI i automatyzacji"
- "Ile epizodów jest w bazie?"

Więcej przykładów: [skills/wise-knowledge-search/EXAMPLES.md](skills/wise-knowledge-search/EXAMPLES.md)

## 🐳 Docker

Projekt używa Docker Compose do uruchomienia Qdrant:

```bash
# Uruchom
cd docker
docker compose up -d

# Sprawdź status
docker compose ps

# Logi
docker compose logs -f

# Zatrzymaj
docker compose down

# Zatrzymaj i usuń dane
docker compose down -v
```

## 🔐 Bezpieczeństwo i prywatność

- ✅ Dane transkryptów przechowywane lokalnie
- ✅ Qdrant hostowany lokalnie
- ✅ Embeddingi generowane przez OpenAI API (text-embedding-3-small)
- ⚠️ Pamiętaj o `.gitignore` dla `.env` i danych osobowych
- ⚠️ Nie commituj plików z `OPENAI_API_KEY`

## 📊 Szczegóły techniczne

### Embeddings
- **Model**: text-embedding-3-small (OpenAI)
- **Wymiary**: 512
- **Distance Metric**: Cosine similarity
- **Batch Size**: 64 sekcje na request
- **Chunking**: 1 sekcja = 1 punkt w Qdrant
- **ID Format**: Auto-incrementing integers (original `{episode_id}_section_{idx}` w payload)

### Komponenty
- **Ingestion**: Python 3.11+, uv, pytest
- **Qdrant**: Docker, localhost:6333 (HTTP), localhost:6334 (gRPC)
- **MCP Server**: Python 3.11+, mcp library, async support
- **MCP Client**: Python 3.11+, Ollama integration, RAG workflow
- **Claude Skill**: MCP tools, Claude Code integration

## 📝 Licencja

Distributed under the MIT License. See `LICENSE` for more information.
