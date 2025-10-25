"""
Wise Knowledge - Podcast Transcripts Vector Search

Main entry point for the application.
"""

from ingest_transcripts import run_ingestion


def main():
    """Main entry point for the Wise Knowledge application."""
    print("🎙️  Wise Knowledge - Podcast Transcripts Vector Search")
    print()

    # Run transcript ingestion pipeline
    run_ingestion()


if __name__ == "__main__":
    main()
