"""Tests for TicketGenerator class."""

import json
import pytest
from qr_ticket_manager import TicketGenerator, TicketGenerationError


class TestTicketGenerator:
    def setup_method(self):
        self.generator = TicketGenerator(secret_key="test-secret-key-123")

    def test_generate_ticket_id_unique(self):
        id1 = self.generator.generate_ticket_id()
        id2 = self.generator.generate_ticket_id()
        assert id1 != id2

    def test_generate_ticket_success(self):
        ticket = self.generator.generate_ticket(
            event_id="evt-001",
            registration_id="reg-001",
            user_id="usr-001",
            event_name="Test Event",
        )
        assert "ticket_id" in ticket
        assert ticket["status"] == "valid"
        assert ticket["payload"]["event_id"] == "evt-001"
        assert ticket["payload"]["user_id"] == "usr-001"
        assert "signature" in ticket

    def test_generate_ticket_missing_fields(self):
        with pytest.raises(TicketGenerationError):
            self.generator.generate_ticket("", "reg-001", "usr-001", "Test")

    def test_create_signature_deterministic(self):
        payload = {"key": "value", "num": 42}
        sig1 = self.generator.create_signature(payload)
        sig2 = self.generator.create_signature(payload)
        assert sig1 == sig2

    def test_create_signature_different_keys(self):
        gen2 = TicketGenerator(secret_key="different-key")
        payload = {"key": "value"}
        assert self.generator.create_signature(payload) != gen2.create_signature(payload)

    def test_create_qr_payload_valid_json(self):
        ticket = self.generator.generate_ticket(
            "evt-001", "reg-001", "usr-001", "Test"
        )
        qr_payload = self.generator.create_qr_payload(ticket)
        data = json.loads(qr_payload)
        assert "ticket_id" in data
        assert "payload" in data
        assert "signature" in data

    def test_empty_secret_key_raises(self):
        with pytest.raises(TicketGenerationError):
            TicketGenerator(secret_key="")
