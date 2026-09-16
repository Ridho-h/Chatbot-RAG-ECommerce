"""
Data ingestion CLI — downloads dataset from Kaggle, processes it,
and builds a persistent FAISS vector store.

Usage:
    python scripts/ingest.py                # Build if not exists
    python scripts/ingest.py --force        # Force rebuild
    python scripts/ingest.py --csv path.csv # Use custom CSV
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.middleware.logging_middleware import configure_structlog


def main():
    configure_structlog()

    import structlog
    logger = structlog.get_logger("ingest")

    parser = argparse.ArgumentParser(description="Ingest product data into FAISS vector store")
    parser.add_argument("--force", action="store_true", help="Force rebuild even if index exists")
    parser.add_argument("--csv", type=str, default=None, help="Path to custom CSV file")
    parser.add_argument("--download", action="store_true", help="Download dataset from Kaggle first")
    args = parser.parse_args()

    csv_path = args.csv or settings.CSV_FILE_PATH

    # Download if requested or CSV doesn't exist
    if args.download or not Path(csv_path).exists():
        logger.info("downloading_dataset")
        try:
            from app.data.loader import download_dataset
            csv_path = download_dataset()
            logger.info("download_complete", path=csv_path)
        except Exception as e:
            logger.error("download_failed", error=str(e))
            print(f"\nERROR: Failed to download dataset: {e}")
            print("Make sure KAGGLE_USERNAME and KAGGLE_KEY are set in your .env file.")
            sys.exit(1)

    # Build the vector store
    logger.info("building_vectorstore", csv_path=csv_path)
    print(f"\n🔄 Uploading vectors to Pinecone from: {csv_path}")
    print("This may take several minutes...")

    try:
        from app.core.vectorstore import build_vectorstore
        # Pinecone does not easily expose index.ntotal via langchain object directly like FAISS
        # So we just report completion
        vectorstore = build_vectorstore(csv_path)
        logger.info("ingestion_complete")
        print(f"\n✅ Ingestion complete!")
        print(f"   Uploaded vectors to Pinecone index: {settings.PINECONE_INDEX_NAME}")
    except FileNotFoundError as e:
        logger.error("csv_not_found", error=str(e))
        print(f"\nERROR: {e}")
        print("Use --download to fetch the dataset from Kaggle first.")
        sys.exit(1)
    except Exception as e:
        logger.error("ingestion_failed", error=str(e))
        print(f"\nERROR: Ingestion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
