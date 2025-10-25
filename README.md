# 🎙️ Wise Knowledge - Podcast Transcripts Vector Search

Inteligentna baza wiedzy z transkryptami podcastów wykorzystująca semantic search w Qdrant. System przetwarza transkrypcje podcastów i umożliwia semantyczne wyszukiwanie treści za pomocą embeddingów OpenAI.

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

## 🏗️ Architektura

```
┌─────────────────────┐
│  transcripts/       │
│  *.json files       │
│  (episode data)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  ingest_transcripts │
│  - Load JSONs       │
│  - OpenAI API       │
│  - Batch processing │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Qdrant Database    │
│  (Vector Store)     │
│  - 512-dim vectors  │
│  - Cosine distance  │
└─────────────────────┘
```

## 🚀 Quick Start

### Wymagania

- Python 3.11+
- Docker & Docker Compose
- OpenAI API Key
- `uv` (dependency manager)

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
└── wise_knowledge/            # Główny pakiet Python
    ├── pyproject.toml         # Zależności (uv)
    ├── .env.example           # Szablon zmiennych środowiskowych
    ├── main.py                # Entry point aplikacji
    └── ingest_transcripts.py  # Logika ingestion
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

## 🔍 Wyszukiwanie (TODO)

Planowane funkcjonalności wyszukiwania:
- Query API do semantycznego przeszukiwania
- Filtrowanie po episode_id, tagach
- Zwracanie najbardziej podobnych sekcji z kontekstem
- Integracja z MCP (Model Context Protocol)

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

- **Embedding Model**: text-embedding-3-small
- **Wymiary**: 512
- **Distance Metric**: Cosine similarity
- **Batch Size**: 64 sekcje na request
- **Chunking**: 1 sekcja = 1 punkt w Qdrant
- **ID Format**: `{episode_id}_section_{idx}`

## 📝 Licencja

Distributed under the MIT License. See `LICENSE` for more information.
