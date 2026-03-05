"""QR code image generation using qrcode and Pillow."""

import io
import qrcode
from qrcode.constants import ERROR_CORRECT_H

from .exceptions import QRCodeGenerationError
from .logger import TicketLogger


class QRCodeCreator:
    """Creates QR code images from ticket payloads.

    Generates high-error-correction QR codes suitable for printing
    and scanning at event entry points.

    Attributes:
        box_size: Size of each box in the QR code grid.
        border: Border size around the QR code.
        logger: Structured logger instance.
    """

    def __init__(self, box_size: int = 10, border: int = 4):
        self.box_size = box_size
        self.border = border
        self.logger = TicketLogger("QRCodeCreator")

    def generate_qr_image(self, data: str) -> bytes:
        """Generate a QR code image as PNG bytes.

        Args:
            data: String data to encode in the QR code.

        Returns:
            PNG image as bytes.

        Raises:
            QRCodeGenerationError: If QR code generation fails.
        """
        if not data:
            raise QRCodeGenerationError("Data must not be empty")

        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ERROR_CORRECT_H,
                box_size=self.box_size,
                border=self.border,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()

            self.logger.info("QR code generated", data_length=len(data),
                             image_size=len(image_bytes))
            return image_bytes

        except Exception as e:
            self.logger.error("QR code generation failed", error=str(e))
            raise QRCodeGenerationError(f"Failed to generate QR code: {e}")

    def generate_qr_base64(self, data: str) -> str:
        """Generate a QR code image as a base64 string.

        Args:
            data: String data to encode in the QR code.

        Returns:
            Base64-encoded PNG image string.
        """
        import base64
        image_bytes = self.generate_qr_image(data)
        return base64.b64encode(image_bytes).decode("utf-8")

    def save_qr_image(self, data: str, file_path: str) -> str:
        """Generate and save a QR code image to a file.

        Args:
            data: String data to encode.
            file_path: Path to save the PNG file.

        Returns:
            The file path where the image was saved.
        """
        image_bytes = self.generate_qr_image(data)
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        self.logger.info("QR code saved", file_path=file_path)
        return file_path
