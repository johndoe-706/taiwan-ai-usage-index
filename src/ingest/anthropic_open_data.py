"""
Anthropic Open Data Ingestion Module for TAUI (Taiwan AI Usage Index).

This module handles the ingestion and processing of Anthropic's open conversation data,
specifically filtering for Taiwan (TWN) and peer countries in the Asia-Pacific region.

The module provides functionality to:
1. Read CSV files from Anthropic's open dataset
2. Filter data for Taiwan and regional peer countries (Singapore, Korea, Japan, Hong Kong)
3. Convert processed data to efficient Parquet format
4. Handle unknown/future columns gracefully for data schema evolution

Privacy and compliance:
- Only processes aggregated, anonymized data from Anthropic's public dataset
- Applies cell suppression rules: <15 conversations OR <5 users → dropped
- No PII processing or storage

Author: TAUI Development Team
License: MIT
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Union, Optional
import warnings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
PEER_COUNTRIES = {'TWN', 'SGP', 'KOR', 'JPN', 'HKG'}
"""Set of Taiwan and peer countries for comparative analysis."""

# Privacy filters as per CLAUDE.md requirements
MIN_CONVERSATIONS = 15
MIN_USERS = 5


def read_anthropic_csv(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Read CSV file from Anthropic's open dataset.

    Args:
        file_path: Path to the CSV file to read

    Returns:
        DataFrame containing the CSV data

    Raises:
        FileNotFoundError: If the specified file does not exist
        pd.errors.ParserError: If the CSV file is malformed

    Example:
        >>> df = read_anthropic_csv('data/raw/anthropic_open/conversations.csv')
        >>> print(f"Loaded {len(df)} rows")
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    logger.info(f"Reading CSV file: {file_path}")

    try:
        # Read CSV with basic error handling and type inference
        df = pd.read_csv(
            file_path,
            encoding='utf-8',
            low_memory=False,  # Prevent DtypeWarning for mixed types
        )

        logger.info(f"Successfully loaded {len(df)} rows and {len(df.columns)} columns")

        # Log column names for debugging (useful for unknown columns)
        logger.debug(f"Columns found: {list(df.columns)}")

        return df

    except pd.errors.ParserError as e:
        logger.error(f"Failed to parse CSV file {file_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading CSV file {file_path}: {e}")
        raise


def filter_taiwan_and_peers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter DataFrame to include only Taiwan and peer countries.

    Filters for countries in the PEER_COUNTRIES set, which includes:
    - TWN (Taiwan)
    - SGP (Singapore)
    - KOR (South Korea)
    - JPN (Japan)
    - HKG (Hong Kong)

    Args:
        df: Input DataFrame with 'country_code' column

    Returns:
        Filtered DataFrame containing only peer countries

    Raises:
        KeyError: If 'country_code' column is not found in DataFrame

    Example:
        >>> df = pd.DataFrame({'country_code': ['TWN', 'USA', 'SGP'], 'count': [1, 2, 3]})
        >>> filtered = filter_taiwan_and_peers(df)
        >>> list(filtered['country_code'])
        ['TWN', 'SGP']
    """
    if df.empty:
        logger.warning("Input DataFrame is empty")
        return df.copy()

    if 'country_code' not in df.columns:
        raise KeyError("DataFrame must contain 'country_code' column")

    logger.info(f"Filtering for peer countries: {PEER_COUNTRIES}")

    # Apply peer country filter
    mask = df['country_code'].isin(PEER_COUNTRIES)
    filtered_df = df[mask].copy()

    # Log filtering results
    original_countries = set(df['country_code'].unique())
    filtered_countries = set(filtered_df['country_code'].unique())

    logger.info(f"Original countries: {original_countries}")
    logger.info(f"Filtered to peer countries: {filtered_countries}")
    logger.info(f"Filtered {len(df)} rows to {len(filtered_df)} rows")

    if filtered_df.empty:
        logger.warning("No peer countries found in dataset")

    return filtered_df


def apply_privacy_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply privacy filters as specified in CLAUDE.md requirements.

    Removes rows where:
    - conversation_count < MIN_CONVERSATIONS (15), OR
    - user_count < MIN_USERS (5)

    Args:
        df: Input DataFrame with conversation and user count columns

    Returns:
        DataFrame with privacy filters applied

    Note:
        If the required columns don't exist, returns the original DataFrame
        with a warning logged.
    """
    if df.empty:
        return df.copy()

    # Check if privacy filter columns exist
    has_conv_count = 'conversation_count' in df.columns
    has_user_count = 'user_count' in df.columns

    if not (has_conv_count or has_user_count):
        logger.warning("No privacy filter columns found (conversation_count, user_count)")
        return df.copy()

    original_count = len(df)
    filtered_df = df.copy()

    # Apply conversation count filter if column exists
    if has_conv_count:
        conv_mask = filtered_df['conversation_count'] >= MIN_CONVERSATIONS
        filtered_df = filtered_df[conv_mask]
        logger.info(f"Conversation filter: {len(filtered_df)} rows remain (>= {MIN_CONVERSATIONS} conversations)")

    # Apply user count filter if column exists
    if has_user_count:
        user_mask = filtered_df['user_count'] >= MIN_USERS
        filtered_df = filtered_df[user_mask]
        logger.info(f"User filter: {len(filtered_df)} rows remain (>= {MIN_USERS} users)")

    removed_count = original_count - len(filtered_df)
    logger.info(f"Privacy filters removed {removed_count} rows ({removed_count/original_count*100:.1f}%)")

    return filtered_df


def convert_to_parquet(df: pd.DataFrame, output_path: Union[str, Path]) -> None:
    """
    Convert DataFrame to Parquet format with optimized settings.

    Args:
        df: DataFrame to convert
        output_path: Path where the Parquet file will be saved

    Raises:
        PermissionError: If unable to write to the specified path
        OSError: If there are other file system issues

    Example:
        >>> df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        >>> convert_to_parquet(df, 'data/interim/open/processed.parquet')
    """
    output_path = Path(output_path)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Converting DataFrame to Parquet: {output_path}")
    logger.info(f"DataFrame shape: {df.shape}")

    try:
        # Write to Parquet with compression for efficiency
        df.to_parquet(
            output_path,
            engine='pyarrow',  # Use pyarrow for best compatibility
            compression='snappy',  # Good balance of speed and compression
            index=False  # Don't write row indices
        )

        # Log file size for monitoring
        file_size = output_path.stat().st_size
        logger.info(f"Successfully wrote Parquet file: {file_size:,} bytes")

    except PermissionError as e:
        logger.error(f"Permission denied writing to {output_path}: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to write Parquet file {output_path}: {e}")
        raise


def process_anthropic_data(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    apply_privacy: bool = True
) -> pd.DataFrame:
    """
    Complete processing pipeline for Anthropic open data.

    This function orchestrates the complete data processing workflow:
    1. Read CSV data from Anthropic's open dataset
    2. Filter for Taiwan and peer countries
    3. Apply privacy filters (optional)
    4. Save processed data as Parquet file

    Args:
        input_path: Path to input CSV file
        output_path: Path for output Parquet file
        apply_privacy: Whether to apply privacy filters (default: True)

    Returns:
        Processed DataFrame (same as saved to Parquet)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If data processing fails
        PermissionError: If unable to write output file

    Example:
        >>> df = process_anthropic_data(
        ...     'data/raw/anthropic_open/conversations.csv',
        ...     'data/interim/open/twn_conversations.parquet'
        ... )
        >>> print(f"Processed {len(df)} records for {df['country_code'].nunique()} countries")
    """
    logger.info("Starting Anthropic data processing pipeline")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")

    try:
        # Step 1: Read raw CSV data
        df = read_anthropic_csv(input_path)

        if df.empty:
            logger.warning("Input file is empty")
            # Still create empty output file for consistency
            convert_to_parquet(df, output_path)
            return df

        # Step 2: Filter for Taiwan and peer countries
        filtered_df = filter_taiwan_and_peers(df)

        if filtered_df.empty:
            logger.warning("No peer country data found after filtering")
            convert_to_parquet(filtered_df, output_path)
            return filtered_df

        # Step 3: Apply privacy filters if requested
        if apply_privacy:
            final_df = apply_privacy_filters(filtered_df)
        else:
            final_df = filtered_df
            logger.info("Skipping privacy filters as requested")

        # Step 4: Save to Parquet format
        convert_to_parquet(final_df, output_path)

        # Final summary
        countries = sorted(final_df['country_code'].unique()) if not final_df.empty else []
        logger.info(f"Processing complete: {len(final_df)} records for countries {countries}")

        return final_df

    except Exception as e:
        logger.error(f"Data processing pipeline failed: {e}")
        raise


def batch_process_anthropic_files(
    input_dir: Union[str, Path],
    output_dir: Union[str, Path],
    file_pattern: str = "*.csv"
) -> dict:
    """
    Process multiple Anthropic CSV files in batch.

    Args:
        input_dir: Directory containing input CSV files
        output_dir: Directory for output Parquet files
        file_pattern: Glob pattern for input files (default: "*.csv")

    Returns:
        Dictionary mapping input filenames to processing results

    Example:
        >>> results = batch_process_anthropic_files(
        ...     'data/raw/anthropic_open/',
        ...     'data/interim/open/'
        ... )
        >>> print(f"Processed {len(results)} files")
    """
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Find all matching CSV files
    csv_files = list(input_dir.glob(file_pattern))

    if not csv_files:
        logger.warning(f"No files found matching pattern '{file_pattern}' in {input_dir}")
        return {}

    logger.info(f"Found {len(csv_files)} files to process")

    results = {}

    for csv_file in csv_files:
        logger.info(f"Processing file: {csv_file.name}")

        # Generate output filename (CSV -> Parquet)
        output_file = output_dir / f"{csv_file.stem}.parquet"

        try:
            df = process_anthropic_data(csv_file, output_file)
            results[csv_file.name] = {
                'status': 'success',
                'rows': len(df),
                'countries': sorted(df['country_code'].unique()) if not df.empty else [],
                'output_file': str(output_file)
            }

        except Exception as e:
            logger.error(f"Failed to process {csv_file.name}: {e}")
            results[csv_file.name] = {
                'status': 'error',
                'error': str(e),
                'output_file': None
            }

    # Summary
    successful = sum(1 for r in results.values() if r['status'] == 'success')
    logger.info(f"Batch processing complete: {successful}/{len(csv_files)} files successful")

    return results


if __name__ == "__main__":
    """
    Command-line interface for testing the ingest module.

    Usage:
        python src/ingest/anthropic_open_data.py input.csv output.parquet
    """
    import sys

    if len(sys.argv) != 3:
        print("Usage: python anthropic_open_data.py <input_csv> <output_parquet>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    try:
        df = process_anthropic_data(input_file, output_file)
        print(f"✅ Successfully processed {len(df)} records")
        print(f"Countries: {sorted(df['country_code'].unique())}")

    except Exception as e:
        print(f"❌ Processing failed: {e}")
        sys.exit(1)