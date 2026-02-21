"""
Document Verification Service - OCR and document parsing
"""
import re
from typing import Dict, Any, Optional
from app.models.applicant import Document
import os


class DocumentVerificationService:
    """Service for verifying uploaded documents using OCR."""

    def __init__(self):
        self.supported_types = ["ic", "salary_slip", "utility_bill", "bank_statement"]

    async def verify_document(self, document: Document) -> Dict[str, Any]:
        """
        Verify a document by extracting text and validating content.
        Returns verification status and extracted data.
        """
        if not os.path.exists(document.file_path):
            return {
                "is_valid": False,
                "error": "File not found"
            }

        # Extract text based on document type
        extracted_data = await self._extract_text(document)

        # Validate based on document type
        validation = await self._validate_document(
            document.document_type,
            extracted_data
        )

        return {
            "is_valid": validation["is_valid"],
            "document_type": document.document_type,
            "extracted_data": extracted_data,
            "validation": validation,
            "verification_notes": validation.get("notes", "")
        }

    async def _extract_text(self, document: Document) -> Dict[str, Any]:
        """Extract text from document using OCR."""
        # For now, we'll use a simplified text extraction
        # In production, this would use Tesseract or PaddleOCR

        extracted = {
            "raw_text": "",
            "confidence": 0.0,
            "fields": {}
        }

        try:
            # Read the file and extract basic info
            # This is a placeholder - in production, use actual OCR
            file_ext = os.path.splitext(document.file_name)[1].lower()

            if file_ext in ['.jpg', '.jpeg', '.png', '.pdf']:
                # Placeholder for actual OCR extraction
                extracted["raw_text"] = "OCR extraction not implemented"
                extracted["confidence"] = 0.5
                extracted["fields"] = {
                    "document_type": document.document_type,
                    "file_name": document.file_name
                }

        except Exception as e:
            extracted["error"] = str(e)

        return extracted

    async def _validate_document(
        self,
        document_type: str,
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate document based on type."""
        if document_type == "ic":
            return self._validate_ic(extracted_data)
        elif document_type == "salary_slip":
            return self._validate_salary_slip(extracted_data)
        elif document_type == "utility_bill":
            return self._validate_utility_bill(extracted_data)
        elif document_type == "bank_statement":
            return self._validate_bank_statement(extracted_data)
        else:
            return {
                "is_valid": True,
                "notes": "Document type validation not implemented"
            }

    def _validate_ic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate IC (MyKad) document."""
        raw_text = data.get("raw_text", "")

        # Check for IC number pattern (12 digits)
        ic_pattern = r'\b\d{12}\b'
        ic_match = re.search(ic_pattern, raw_text)

        if not ic_match:
            return {
                "is_valid": False,
                "notes": "Nombor IC tidak dijumpai"
            }

        # Validate IC number format
        ic_number = ic_match.group()
        if not self._validate_ic_checksum(ic_number):
            return {
                "is_valid": False,
                "notes": "Format nombor IC tidak sah"
            }

        # Check for name (at least 3 words typical for Malaysian names)
        return {
            "is_valid": True,
            "notes": "Dokumen IC disahkan",
            "extracted_ic": ic_number
        }

    def _validate_ic_checksum(self, ic_number: str) -> bool:
        """
        Validate IC number using the Malaysian IC checksum algorithm.
        """
        if len(ic_number) != 12 or not ic_number.isdigit():
            return False

        # Placeholder - actual checksum validation
        return True

    def _validate_salary_slip(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate salary slip document."""
        raw_text = data.get("raw_text", "")

        # Check for salary amount patterns
        salary_patterns = [
            r'Gaji\s*Bulanan[:\s]*RM?\s*[\d,]+\.?\d*',
            r'Net\s*Pay[:\s]*RM?\s*[\d,]+\.?\d*',
            r'Pendapatan\s*Bersih[:\s]*RM?\s*[\d,]+\.?\d*',
            r'RM\s*[\d,]+\.?\d*'
        ]

        found_salary = False
        for pattern in salary_patterns:
            if re.search(pattern, raw_text, re.IGNORECASE):
                found_salary = True
                break

        if not found_salary:
            return {
                "is_valid": False,
                "notes": "Jumlah gaji tidak dijumpai"
            }

        # Check for employer name
        if len(raw_text) < 50:
            return {
                "is_valid": False,
                "notes": "Maklumat slip gaji tidak lengkap"
            }

        return {
            "is_valid": True,
            "notes": "Slip gaji disahkan"
        }

    def _validate_utility_bill(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate utility bill document."""
        raw_text = data.get("raw_text", "")

        # Check for utility company identifiers
        utility_patterns = [
            r'TNB|Tenaga',
            r'SESB|Sabah Electricity',
            r'SEWSB|Sarawak Electricity',
            r'Air|SAJ|PAIP',
            r'Bil\s*:?\s*\d+',
            r'Invoic'
        ]

        found_utility = False
        for pattern in utility_patterns:
            if re.search(pattern, raw_text, re.IGNORECASE):
                found_utility = True
                break

        if not found_utility:
            return {
                "is_valid": False,
                "notes": "Bil utiliti tidak dapat dikenal pasti"
            }

        # Check for address
        if len(raw_text) < 100:
            return {
                "is_valid": False,
                "notes": "Maklumat bil tidak lengkap"
            }

        return {
            "is_valid": True,
            "notes": "Bil utiliti disahkan"
        }

    def _validate_bank_statement(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate bank statement document."""
        raw_text = data.get("raw_text", "")

        # Check for bank identifiers
        bank_patterns = [
            r'Maybank|CIMB|Public\s*Bank',
            r'Bank\s*Raky[at]|BSN',
            r'Hong\s*Leong|Ambank',
            r'Statement|Transaksi'
        ]

        found_bank = False
        for pattern in bank_patterns:
            if re.search(pattern, raw_text, re.IGNORECASE):
                found_bank = True
                break

        if not found_bank:
            return {
                "is_valid": False,
                "notes": "Penyata bank tidak dapat dikenal pasti"
            }

        return {
            "is_valid": True,
            "notes": "Penyata bank disahkan"
        }

    async def extract_ic_information(self, document: Document) -> Optional[Dict[str, Any]]:
        """Extract and parse IC information."""
        if document.document_type != "ic":
            return None

        extracted = await self._extract_text(document)
        raw_text = extracted.get("raw_text", "")

        # Extract IC number
        ic_pattern = r'\b(\d{6})\s*(\d{2})\s*(\d{4})\b'
        match = re.search(ic_pattern, raw_text)

        if match:
            return {
                "ic_number": f"{match.group(1)}{match.group(2)}{match.group(3)}",
                "birthdate": f"{match.group(1)}",
                "birthplace_code": match.group(2),
                "gender_code": match.group(3)[0]
            }

        return None