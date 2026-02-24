from backend.app.canonical_json import canonicalize
from backend.app.ledger import sha256_hex

def test_canonical_json_is_deterministic():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonicalize(a) == canonicalize(b)

def test_sha256_known_vector():
    # standard known vector for sha256("abc")
    assert sha256_hex(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
