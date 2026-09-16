"""
Dataset loader — downloads from Kaggle and converts CSV rows into LangChain Documents.
"""

import os
from pathlib import Path

import pandas as pd
import structlog
from langchain_core.documents import Document

from app.config import settings

logger = structlog.get_logger(__name__)


def download_dataset(target_dir: str | None = None) -> str:
    """
    Download the Amazon Sales dataset from Kaggle.

    Args:
        target_dir: Directory to download into. Defaults to backend/data/.

    Returns:
        Path to the extracted CSV file.

    Raises:
        RuntimeError: If download or extraction fails.
    """
    target_dir = target_dir or str(Path(settings.CSV_FILE_PATH).parent)
    os.makedirs(target_dir, exist_ok=True)

    # Set Kaggle credentials
    if settings.KAGGLE_USERNAME and settings.KAGGLE_KEY:
        os.environ["KAGGLE_USERNAME"] = settings.KAGGLE_USERNAME
        os.environ["KAGGLE_KEY"] = settings.KAGGLE_KEY

    logger.info("downloading_dataset", dataset=settings.DATASET_NAME, target=target_dir)

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi

        api = KaggleApi()
        api.authenticate()
        api.dataset_download_files(
            settings.DATASET_NAME,
            path=target_dir,
            unzip=True,
        )
        logger.info("dataset_downloaded", target=target_dir)
    except Exception as e:
        raise RuntimeError(f"Failed to download dataset: {e}") from e

    csv_path = settings.CSV_FILE_PATH
    if not Path(csv_path).exists():
        # Try to find the CSV file in the target directory
        csv_files = list(Path(target_dir).glob("*.csv"))
        if csv_files:
            csv_path = str(csv_files[0])
        else:
            raise RuntimeError(f"No CSV file found in {target_dir} after download")

    return csv_path


def load_documents(csv_path: str | None = None) -> list[Document]:
    """
    Load product data from CSV and convert each row into a LangChain Document.

    Each document contains:
        - page_content: product name, category, and description (for embedding)
        - metadata: price, rating, rating count, product link (for display)

    Args:
        csv_path: Path to the CSV file. Defaults to settings.CSV_FILE_PATH.

    Returns:
        List of LangChain Document objects.
    """
    csv_path = csv_path or settings.CSV_FILE_PATH

    if not Path(csv_path).exists():
        raise FileNotFoundError(
            f"CSV file not found at {csv_path}. "
            "Run the ingestion script first: python scripts/ingest.py"
        )

    logger.info("loading_csv", path=csv_path)
    df = pd.read_csv(csv_path)

    # Select and clean relevant columns
    required_cols = ["product_name", "category", "about_product"]
    optional_cols = ["discounted_price", "rating", "rating_count", "product_link"]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in CSV")

    df_cleaned = df[
        [c for c in required_cols + optional_cols if c in df.columns]
    ].copy()

    # Drop rows missing essential content
    df_cleaned = df_cleaned.dropna(subset=required_cols)
    df_cleaned = df_cleaned.fillna("N/A")

    # Convert each row to a Document
    docs = []
    for _, row in df_cleaned.iterrows():
        page_content = (
            f"Product Name: {row['product_name']}\n"
            f"Category: {row['category']}\n"
            f"About Product: {row['about_product']}"
        )

        metadata = {
            "product_name": str(row.get("product_name", "N/A")),
            "discounted_price": str(row.get("discounted_price", "N/A")),
            "rating": str(row.get("rating", "N/A")),
            "rating_count": str(row.get("rating_count", "N/A")),
            "product_link": str(row.get("product_link", "N/A")),
        }

        docs.append(Document(page_content=page_content, metadata=metadata))

    logger.info("documents_created", count=len(docs))
    return docs
