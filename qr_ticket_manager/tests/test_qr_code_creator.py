"""Tests for QRCodeCreator class."""

import base64
import os
import tempfile
import pytest
from qr_ticket_manager import QRCodeCreator, QRCodeGenerationError


class TestQRCodeCreator:
    def setup_method(self):
        self.creator = QRCodeCreator(box_size=5, border=2)

    def test_generate_qr_image_returns_bytes(self):
        result = self.creator.generate_qr_image("test data")
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG magic bytes
        assert result[:4] == b"\x89PNG"

    def test_generate_qr_image_empty_data(self):
        with pytest.raises(QRCodeGenerationError):
            self.creator.generate_qr_image("")

    def test_generate_qr_base64(self):
        result = self.creator.generate_qr_base64("test data")
        assert isinstance(result, str)
        decoded = base64.b64decode(result)
        assert decoded[:4] == b"\x89PNG"

    def test_save_qr_image(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            path = f.name
        try:
            result = self.creator.save_qr_image("test data", path)
            assert result == path
            assert os.path.exists(path)
            with open(path, "rb") as f:
                assert f.read(4) == b"\x89PNG"
        finally:
            os.unlink(path)

    def test_different_data_different_images(self):
        img1 = self.creator.generate_qr_image("data one")
        img2 = self.creator.generate_qr_image("data two")
        assert img1 != img2
