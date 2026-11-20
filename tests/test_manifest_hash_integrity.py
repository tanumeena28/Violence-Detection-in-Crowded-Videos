import hashlib
def test_hash():
    assert len(hashlib.sha256(b"test").hexdigest()) == 64
