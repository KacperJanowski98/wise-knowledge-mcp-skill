# Wise Knowledge MCP Client

Prosty klient testowy do serwera MCP z bazą wiedzy podcastów. Używa lokalnego modelu Ollama do generowania odpowiedzi na podstawie wyszukanych treści.

## Wymagania

1. **Ollama** - lokalny serwer LLM
2. **Python 3.11+**
3. **Działający serwer MCP** (`mcp_server/`)
4. **Baza Qdrant** z zaindeksowanymi transkryptami

## Instrukcje

### 1. Zainstaluj zależności klienta

```bash
cd mcp_client
uv sync
```

### 2. Skonfiguruj środowisko

```bash
cp .env.example .env
```

## Uruchomienie

### Upewnij się, że wszystko działa:

1. **Qdrant** (w katalogu `docker/`):
```bash
cd ../docker
docker compose up -d
```

2. **Baza wiedzy zaindeksowana** (w katalogu `wise_knowledge/`):
```bash
cd ../wise_knowledge
uv run python main.py
```

3. **Ollama** działa:
```bash
ollama list  # sprawdz dostępne modele
```

### Uruchom klienta:

```bash
cd mcp_client
uv run python main.py
```

## Użycie

Po uruchomieniu klienta zobaczysz interaktywny interfejs:

```
================================================================================
< Wise Knowledge - Interactive Chat
================================================================================
Ask questions about podcast content. Type 'exit' to quit.
Type 'status' to check collection status.
================================================================================

S Your question:
```

### PrzykBadowe pytania:

```
S Your question: Jak zbudować strategię biznesową?

S Your question: Co to jest dzwignia w biznesie?

S Your question: Jak pozyskiwać klientów?

S Your question: status
```

### Komendy specjalne:

- `status` - Wyświetla status kolekcji w Qdrant (liczba punktów, status)
- `exit`, `quit`, `q` - Wyjście z programu

## Jak to dziaBa

1. **Pytanie u|ytkownika** - Klient wysyła pytanie do serwera MCP
2. **Semantic search** - Serwer wyszukuje najbardziej podobne sekcje (domyślnie score_threshold=0.7)
3. **Kontekst** - Znalezione sekcje są formatowane jako kontekst
4. **LLM (Ollama)** - Model generuje odpowiedz na podstawie kontekstu
5. **Odpowiedz** - Użytkownik otrzymuje streaming odpowiedzi od modelu

## Konfiguracja

Edytuj `.env` aby zmienić:

```bash
# Model Ollama (domy[lnie llama3.2:latest)
OLLAMA_MODEL=mistral:latest

# URL Ollama (domy[lnie http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434

# Zcie|ka do serwera MCP (domy[lnie ../mcp_server)
MCP_SERVER_DIR=/path/to/mcp_server
```

## Rozwiązywanie problemów

### "Ollama is not running"
```bash
# Uruchom Ollama w tle
ollama serve
```

### "Connection refused to Qdrant"
```bash
# Uruchom Qdrant
cd ../docker
docker compose up -d

# Sprawdz status
docker compose ps
```

### "Collection not found"
```bash
# Zaindeksuj transkrypty
cd ../wise_knowledge
uv run python main.py
```

### "No relevant results found"
- Spróbuj innego pytania
- Sprawdz czy baza jest zaindeksowana: wpisz `status`
- Score threshold mo|e być za wysoki (domy[lnie 0.7)

## Licencja

MIT
