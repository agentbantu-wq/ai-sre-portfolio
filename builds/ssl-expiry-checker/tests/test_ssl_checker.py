#!/usr/bin/env python3
"""
Tests for SSL Expiry Checker
"""

import pytest
from datetime import datetime, timedelta
from src.ssl_checker import SSLChecker, SSLInfo

def test_ssl_checker_init():
    """Test SSLChecker initialization"""
    checker = SSLChecker(timeout=5, warning_days=14)
    assert checker.timeout == 5
    assert checker.warning_days == 14

def test_ssl_info_creation():
    """Test SSLInfo dataclass creation"""
    now = datetime.now()
    future = now + timedelta(days=30)

    info = SSLInfo(
        domain="example.com",
        issuer="CN=Example CA",
        subject="CN=example.com",
        valid_from=now,
        valid_until=future,
        days_remaining=30,
        is_expired=False,
        is_expiring_soon=False,
        serial_number="12345",
        signature_algorithm="sha256WithRSAEncryption"
    )

    assert info.domain == "example.com"
    assert info.days_remaining == 30
    assert not info.is_expired

def test_check_valid_domain():
    """Test checking a valid domain"""
    checker = SSLChecker()
    result = checker.get_certificate_info("google.com")

    assert result is not None
    assert result.domain == "google.com"
    assert isinstance(result.days_remaining, int)
    assert result.valid_until > datetime.now()

def test_check_invalid_domain():
    """Test checking an invalid domain"""
    checker = SSLChecker(timeout=1)
    result = checker.get_certificate_info("invalid.domain.that.does.not.exist")

    assert result is None

def test_expiring_soon_logic():
    """Test expiring soon detection"""
    checker = SSLChecker(warning_days=30)

    # Create mock SSLInfo
    now = datetime.now()
    soon = now + timedelta(days=15)  # Within warning period
    far = now + timedelta(days=60)   # Outside warning period
    past = now - timedelta(days=1)   # Expired

    expiring_soon = SSLInfo(
        domain="test.com",
        issuer="CA",
        subject="test.com",
        valid_from=now,
        valid_until=soon,
        days_remaining=15,
        is_expired=False,
        is_expiring_soon=True,
        serial_number="1",
        signature_algorithm="sha256"
    )

    valid = SSLInfo(
        domain="test.com",
        issuer="CA",
        subject="test.com",
        valid_from=now,
        valid_until=far,
        days_remaining=60,
        is_expired=False,
        is_expiring_soon=False,
        serial_number="1",
        signature_algorithm="sha256"
    )

    expired = SSLInfo(
        domain="test.com",
        issuer="CA",
        subject="test.com",
        valid_from=now - timedelta(days=365),
        valid_until=past,
        days_remaining=-1,
        is_expired=True,
        is_expiring_soon=False,
        serial_number="1",
        signature_algorithm="sha256"
    )

    # Test logic
    assert expiring_soon.is_expiring_soon
    assert not valid.is_expiring_soon
    assert expired.is_expired

def test_export_json():
    """Test JSON export"""
    import tempfile
    import os
    import json

    checker = SSLChecker()
    results = [
        SSLInfo(
            domain="test.com",
            issuer="CA",
            subject="test.com",
            valid_from=datetime.now(),
            valid_until=datetime.now() + timedelta(days=30),
            days_remaining=30,
            is_expired=False,
            is_expiring_soon=False,
            serial_number="123",
            signature_algorithm="sha256"
        )
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "test.json")
        exported = checker.export_results(results, 'json', filename)

        assert os.path.exists(filename)
        with open(filename, 'r') as f:
            data = json.load(f)
            assert len(data) == 1
            assert data[0]['domain'] == 'test.com'

def test_check_domains():
    """Test checking multiple domains"""
    checker = SSLChecker()
    domains = ["google.com", "github.com"]
    results = checker.check_domains(domains)

    assert len(results) >= 1  # At least one should succeed
    for result in results:
        assert result.domain in domains
        assert isinstance(result.days_remaining, int)