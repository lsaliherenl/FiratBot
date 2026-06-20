"""Sirlari Windows DPAPI ile sifreler/cozer (ek bagimlilik yok, sadece ctypes).

CryptProtectData ile sifrelenen veri yalnizca AYNI Windows kullanicisi tarafindan
(ayni makinede) cozulebilir. settings.json'da sifre/token bu sekilde saklanir;
dosyada duz metin parola bulunmaz.
"""
from __future__ import annotations

import base64
import ctypes
from ctypes import wintypes


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]


_crypt32 = ctypes.windll.crypt32
_kernel32 = ctypes.windll.kernel32


def _to_blob(data: bytes) -> _DATA_BLOB:
    buf = ctypes.create_string_buffer(data, len(data))
    return _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char)))


def _from_blob(blob: _DATA_BLOB) -> bytes:
    size = int(blob.cbData)
    out = ctypes.create_string_buffer(size)
    ctypes.memmove(out, blob.pbData, size)
    return out.raw


def protect(plaintext: str) -> str:
    """Metni DPAPI ile sifreler, base64 string dondurur."""
    blob_in = _to_blob(plaintext.encode("utf-8"))
    blob_out = _DATA_BLOB()
    ok = _crypt32.CryptProtectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    )
    if not ok:
        raise OSError("CryptProtectData basarisiz oldu")
    try:
        return base64.b64encode(_from_blob(blob_out)).decode("ascii")
    finally:
        _kernel32.LocalFree(blob_out.pbData)


def unprotect(token_b64: str) -> str:
    """protect() ciktisini cozer, orijinal metni dondurur."""
    blob_in = _to_blob(base64.b64decode(token_b64))
    blob_out = _DATA_BLOB()
    ok = _crypt32.CryptUnprotectData(
        ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)
    )
    if not ok:
        raise OSError("CryptUnprotectData basarisiz oldu (farkli kullanici/makine olabilir)")
    try:
        return _from_blob(blob_out).decode("utf-8")
    finally:
        _kernel32.LocalFree(blob_out.pbData)
