"""
Amplitude API integration service.
Provides functions to fetch and process user feedback data from Amplitude.
"""

from .client import AmplitudeClient
from .data_processor import save_data_to_file, process_raw_file, prepare_for_vectorization
from .query_builder import build_query, build_export_query, build_event_payload

__all__ = [
    'AmplitudeClient',
    'save_data_to_file',
    'process_raw_file',
    'prepare_for_vectorization',
    'build_query',
    'build_export_query',
    'build_event_payload'
]
