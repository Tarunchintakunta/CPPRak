"""Tests for TicketValidator class."""

import json
import pytest
from qr_ticket_manager import (
    TicketGenerator,
    TicketValidator,
    InvalidSignatureError,
    TicketAlreadyUsedError,
    TicketRevokedError,
    TicketValidationError,
)


class TestTicketValidator:
    def setup_method(self):
        self.secret = "test-secret-key-123"
        self.generator = TicketGenerator(secret_key=self.secret)
        self.validator = TicketValidator(secret_key=self.secret)

    def _make_qr_data(self):
        ticket = self.generator.generate_ticket(
            "evt-001", "reg-001", "usr-001", "Test Event"
        )
        return self.generator.create_qr_payload(ticket), ticket

    def test_validate_valid_ticket(self):
        qr_data, _ = self._make_qr_data()
        result = self.validator.validate_ticket(qr_data)
        assert result["valid"] is True

    def test_invalid_signature_rejected(self):
        qr_data, _ = self._make_qr_data()
        data = json.loads(qr_data)
        data["signature"] = "tampered_signature"
        with pytest.raises(InvalidSignatureError):
            self.validator.validate_ticket(json.dumps(data))

    def test_tampered_payload_rejected(self):
        qr_data, _ = self._make_qr_data()
        data = json.loads(qr_data)
        data["payload"]["event_id"] = "evt-hacked"
        with pytest.raises(InvalidSignatureError):
            self.validator.validate_ticket(json.dumps(data))

    def test_wrong_key_rejected(self):
        qr_data, _ = self._make_qr_data()
        wrong_validator = TicketValidator(secret_key="wrong-key")
        with pytest.raises(InvalidSignatureError):
            wrong_validator.validate_ticket(qr_data)

    def test_used_ticket_rejected(self):
        qr_data, _ = self._make_qr_data()
        result = self.validator.validate_ticket(
            qr_data, get_ticket_status=lambda tid: "used"
        )
        # Should not reach here
        assert False
    test_used_ticket_rejected = pytest.mark.xfail(
        raises=TicketAlreadyUsedError)(test_used_ticket_rejected)

    def test_revoked_ticket_rejected(self):
        qr_data, _ = self._make_qr_data()
        with pytest.raises(TicketRevokedError):
            self.validator.validate_ticket(
                qr_data, get_ticket_status=lambda tid: "revoked"
            )

    def test_invalid_json_rejected(self):
        with pytest.raises(TicketValidationError):
            self.validator.validate_ticket("not valid json")

    def test_missing_fields_rejected(self):
        with pytest.raises(TicketValidationError):
            self.validator.validate_ticket(json.dumps({"ticket_id": "abc"}))

    def test_check_status_valid(self):
        assert self.validator.check_status("valid") is True

    def test_check_status_used(self):
        with pytest.raises(TicketAlreadyUsedError):
            self.validator.check_status("used")
