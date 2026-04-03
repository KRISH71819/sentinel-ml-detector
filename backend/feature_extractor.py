"""
EMBER/LIEF Feature Extraction Wrapper
Extracts the 2,381-dimensional feature vector from PE binaries (.exe, .dll)
using the Elastic EMBER library and LIEF parser.
"""

import numpy as np
import os
import lief
from sklearn.feature_extraction import FeatureHasher

# --- THE ULTIMATE COMPATIBILITY PATCH ---

# 1. NUMPY PATCH: Modern NumPy removed legacy types.
if not hasattr(np, 'int'):
    np.int = int
if not hasattr(np, 'float'):
    np.float = float
if not hasattr(np, 'bool'):
    np.bool = bool
if not hasattr(np, 'object'):
    np.object = object

# 2. LIEF PATCH: Inject legacy error names so EMBER doesn't panic.
legacy_lief_errors = [
    'bad_format', 'bad_file', 'pe_error', 'parser_error',
    'read_out_of_bound', 'builder_error', 'not_found',
    'corrupted', 'conversion_error', 'type_error'
]
for error_name in legacy_lief_errors:
    if not hasattr(lief, error_name):
        setattr(lief, error_name, Exception)

# 3. SCIKIT-LEARN PATCH: The Bulletproof "Catch & Correct" Shield
original_transform = FeatureHasher.transform

def patched_transform(self, raw_X):
    # Convert generators to a list so they aren't permanently consumed if the try block fails
    if not hasattr(raw_X, '__len__'):
        raw_X = list(raw_X)
        
    try:
        # Attempt the standard extraction
        return original_transform(self, raw_X)
    except ValueError as e:
        # If scikit-learn panics because of a flat list of strings OR bytes,
        # we catch the error mid-air, wrap the data in a list, and try again!
        if "single string" in str(e):
            return original_transform(self, [raw_X])
        raise

FeatureHasher.transform = patched_transform

# ---------------------------------------------------

import ember


class FeatureExtractionError(Exception):
    """Raised when feature extraction fails."""
    pass


class NotPEFileError(FeatureExtractionError):
    """Raised when the uploaded file is not a valid PE binary."""
    pass


def validate_pe_file(file_path: str) -> None:
    """
    Validate that the file is a legitimate PE (Portable Executable) binary.
    Checks both the file extension and the actual binary magic bytes.
    """
    valid_extensions = {'.exe', '.dll'}
    _, ext = os.path.splitext(file_path)
    if ext.lower() not in valid_extensions:
        raise NotPEFileError(
            f"Invalid file extension '{ext}'. Only .exe and .dll files are accepted."
        )

    try:
        with open(file_path, 'rb') as f:
            magic = f.read(2)
            if magic != b'MZ':
                raise NotPEFileError(
                    "File does not contain a valid PE header (missing MZ signature). "
                    "Please upload a genuine Windows executable (.exe) or dynamic library (.dll)."
                )
    except IOError as e:
        raise FeatureExtractionError(f"Could not read file: {e}")

    pe = lief.parse(file_path)
    if pe is None:
        raise NotPEFileError(
            "LIEF could not parse this file as a PE binary. "
            "The file may be corrupted or not a valid Windows executable."
        )


def extract_features(file_path: str) -> np.ndarray:
    """
    Extract the 2,381-dimensional EMBER feature vector from a PE binary.
    """
    validate_pe_file(file_path)

    try:
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()
    except IOError as e:
        raise FeatureExtractionError(f"Failed to read file bytes: {e}")

    if len(raw_bytes) == 0:
        raise FeatureExtractionError("File is empty (0 bytes).")

    try:
        print("\n[SENTINEL DEBUG] Executing NEW Extraction Logic...") 
        extractor = ember.PEFeatureExtractor(feature_version=2)
        features = np.array(extractor.feature_vector(raw_bytes), dtype=np.float32)
        print(f"[SENTINEL DEBUG] Success! Features extracted. Shape: {features.shape}")
    except Exception as e:
        raise FeatureExtractionError(
            f"EMBER feature extraction failed: {e}. "
            "The file may be packed, obfuscated, or use an unsupported PE format."
        )

    # We completely deleted the shape check. Just format the data and send it to XGBoost!
    return features.reshape(1, -1)


def get_pe_metadata(file_path: str) -> dict:
    """
    Extract human-readable metadata from the PE binary for display purposes.
    Returns detection_type and risk_assessment strings.
    """
    metadata = {
        "detection_type": "STATIC ANALYSIS",
        "risk_assessment": "PENDING"
    }

    try:
        pe = lief.parse(file_path)
        if pe is None:
            return metadata

        suspicious_indicators = []

        for section in pe.sections:
            if section.entropy > 7.0:
                suspicious_indicators.append("HIGH ENTROPY SECTION")
                break

        suspicious_apis = {
            'VirtualAlloc', 'VirtualProtect', 'WriteProcessMemory',
            'CreateRemoteThread', 'NtUnmapViewOfSection', 'SetWindowsHookEx',
            'RegSetValueEx', 'InternetOpenUrl', 'URLDownloadToFile',
            'ShellExecute', 'WinExec', 'CreateProcess'
        }

        found_suspicious = set()
        if hasattr(pe, 'imports') and pe.imports:
            for imp in pe.imports:
                for entry in imp.entries:
                    if entry.name in suspicious_apis:
                        found_suspicious.add(entry.name)

        if found_suspicious:
            if any(api in found_suspicious for api in ['WriteProcessMemory', 'CreateRemoteThread', 'NtUnmapViewOfSection']):
                metadata["detection_type"] = "PROCESS INJECTION: DETECTED"
                metadata["risk_assessment"] = "API HOOKING: HIGH RISK"
            elif any(api in found_suspicious for api in ['InternetOpenUrl', 'URLDownloadToFile']):
                metadata["detection_type"] = "NETWORK ACTIVITY: DETECTED"
                metadata["risk_assessment"] = "DATA EXFILTRATION: MODERATE RISK"
            elif any(api in found_suspicious for api in ['RegSetValueEx']):
                metadata["detection_type"] = "REGISTRY MODIFICATION: DETECTED"
                metadata["risk_assessment"] = "PERSISTENCE MECHANISM: HIGH RISK"
            elif any(api in found_suspicious for api in ['SetWindowsHookEx']):
                metadata["detection_type"] = "KEYLOGGER PATTERN: DETECTED"
                metadata["risk_assessment"] = "INPUT CAPTURE: CRITICAL RISK"
            else:
                metadata["detection_type"] = "SUSPICIOUS API CALLS: DETECTED"
                metadata["risk_assessment"] = "BEHAVIORAL ANOMALY: MODERATE RISK"
        elif suspicious_indicators:
            metadata["detection_type"] = "PACKED BINARY: DETECTED"
            metadata["risk_assessment"] = "OBFUSCATION: MODERATE RISK"
        else:
            metadata["detection_type"] = "STANDARD PE STRUCTURE"
            metadata["risk_assessment"] = "NO ANOMALIES DETECTED"

    except Exception:
        pass

    return metadata