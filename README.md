# 🎙️ Podcast Knowledge Base MCP

Inteligentna baza wiedzy z transkryptami podcastów wykorzystująca semantic search i protokół MCP (Model Context Protocol) dla bezpośredniej integracji z Claude AI.

## 📋 Opis projektu

System umożliwiający budowę prywatnej bazy wiedzy z transkryptów podcastów z wykorzystaniem wyszukiwania semantycznego. Projekt łączy:
- **Qdrant** - bazę wektorową do przechowywania embeddingów
- **MCP Server** - serwer protokołu Model Context Protocol
- **OpenAI Embeddings** - do generowania reprezentacji wektorowych
- **Claude Skills** - niestandardowe instrukcje dla Claude AI

Dzięki temu Claude może inteligentnie przeszukiwać i analizować treści podcastów, odpowiadając na pytania kontekstowe i znajdując powiązane informacje.

## ✨ Funkcjonalności

- 🔍 **Semantic Search** - wyszukiwanie podobieństw semantycznych, nie tylko słów kluczowych
- 📊 **Strukturyzowane metadane** - integracja danych JSON z dodatkowymi informacjami o epizodach
- 🎯 **Inteligentny chunking** - automatyczny podział długich transkryptów na optymalne fragmenty
- 🔗 **Natywna integracja z Claude** - bezpośredni dostęp przez protokół MCP
- 🏷️ **Zaawansowane filtrowanie** - po podcastach, datach, tematach, mówcach
- ⚡ **Szybkie wyszukiwanie** - milisekundowe odpowiedzi dzięki indeksom wektorowym
- 📝 **Cytowanie źródeł** - automatyczne linkowanie do konkretnych epizodów i timestampów

## 🏗️ Architektura

```
┌─────────────────────┐
│  Transkrypty .md   │
│  Metadane .json     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Import Script      │
│  - Chunking         │
│  - Embeddings API   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Qdrant             │
│  (Vector Database)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  MCP Server         │
│  - search_podcasts  │
│  - get_insights     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Claude AI          │
│  + Custom Skill     │
└─────────────────────┘
```

## 🔐 Bezpieczeństwo i prywatność

- ✅ Dane transkryptów przechowywane lokalnie
- ✅ Embeddingi mogą być generowane lokalnie (Ollama)
- ✅ Qdrant można hostować samodzielnie
- ✅ MCP server działa lokalnie
- ⚠️ Pamiętaj o .gitignore dla .env i danych osobowych


## 📝 Licencja

Distributed under the MIT License. See `LICENSE` for more information.
