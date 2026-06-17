#!/usr/bin/env python3
"""
Extract NES game codes from PDF manuals using OCR.
Codes are typically in the upper right corner (e.g., NES-B5-ESP)
"""

import os
import re
import json
import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image
import pytesseract

# Configuration
MANUALS_DIR = Path("./manuals")
OUTPUT_FILE = Path("./game_codes.json")
DPI = 300  # Higher DPI for better OCR accuracy
TEST_MODE = False  # Set to False to process all PDFs
MAX_TEST_FILES = 20  # Number of files to test


def extract_code_from_pdf(pdf_path):
    """
    Extract the NES code from the upper right corner of the first page.
    Returns the code if found, None otherwise.
    """
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)

        if len(doc) == 0:
            print(f"  ⚠️  No pages in PDF")
            return None

        # Get the first page
        page = doc[0]

        # Get page dimensions
        rect = page.rect
        width = rect.width
        height = rect.height

        # Define the upper right corner area (top 15% of page, right 20% of width)
        # Adjust these percentages if needed based on manual layout
        crop_rect = fitz.Rect(
            width * 0.8,  # Start at 80% from left (rightmost 20%)
            0,            # Top of page
            width,        # Right edge
            height * 0.15  # 15% down from top
        )

        # Render the cropped area to an image
        mat = fitz.Matrix(DPI/72, DPI/72)  # Scale to DPI
        pix = page.get_pixmap(matrix=mat, clip=crop_rect)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Perform OCR with different configs for better accuracy
        configs = [
            '--psm 6',  # Assume uniform block of text
            '--psm 7',  # Treat image as single text line
            '--psm 11', # Sparse text
        ]

        all_text = []
        for config in configs:
            text = pytesseract.image_to_string(img, lang='eng', config=config)
            all_text.append(text)

        combined_text = ' '.join(all_text)

        # Clean up common OCR errors
        # Replace common misreads: 0->O, O->0, etc.
        cleaned_text = combined_text.replace('Nes', 'NES').replace('nes', 'NES')
        # Replace common separator misreads: ~ -> -, = -> -, | -> -
        cleaned_text = cleaned_text.replace('~', '-').replace('=', '-').replace('|', '-')

        # Look for NES code pattern (e.g., NES-B5-ESP, NES-AA-FRG, NES-XX-NOE)
        # Pattern: NES-XX-CCC where XX is 1-3 alphanumeric chars and CCC is country code
        # Be flexible with separators (-, space, or nothing)
        # Common country codes: ESP (Spain), FRG (Germany/West Germany), NOE (Austria),
        # EUR (Europe), UKV (UK), HOL (Netherlands), ITA (Italy), FRA (France), SWE (Sweden)
        patterns = [
            r'NES[- ]?[A-Z0-9]{1,3}[- ]?(ESP|FRG|NOE|EUR|UKV|HOL|ITA|FRA|SWE|SCN|FAH|FRN|EEC|AUS)',  # All country codes
            r'NES[- ]?[A-Z0-9]{1,3}[- ]?SPA',  # Sometimes Spanish is SPA
            r'NES[- ]?[A-Z0-9]{1,3}[- ]?ESE',  # Common OCR error: ESP -> ESE
            r'NES[- ]?[A-Z0-9IOl]{1,3}[- ]?(ESP|FRG|NOE|EUR)',  # Allow common OCR confusions (I/1, O/0, l/1)
        ]

        for pattern in patterns:
            match = re.search(pattern, cleaned_text, re.IGNORECASE)
            if match:
                code = match.group(0).upper()
                # Normalize the code format to NES-XX-ESP
                code = re.sub(r'\s+', '-', code)  # Replace spaces with hyphens
                # Fix common OCR errors
                code = code.replace('ESE', 'ESP')  # Common OCR error
                # Ensure proper format
                if not re.match(r'NES-[A-Z0-9]{1,3}-(ESP|FRG|NOE|EUR|UKV|HOL|ITA|FRA|SWE|SPA|SCN|FAH|FRN|EEC|AUS)', code):
                    parts = re.split(r'[-\s]', code)
                    if len(parts) >= 3:
                        code = f"{parts[0]}-{parts[1]}-{parts[2]}"
                doc.close()
                return code

        # If no match, print the OCR text for debugging
        print(f"  🔍 OCR text: {combined_text.strip()[:100]}")

        doc.close()
        return None

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None


def main():
    """Extract codes from all PDF manuals."""

    # Check if tesseract is installed
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        print("❌ Tesseract OCR is not installed!")
        print("Install it with: sudo dnf install tesseract tesseract-langpack-eng")
        print("Or: sudo apt install tesseract-ocr")
        return

    print("NES Game Code Extractor")
    print("=" * 60)
    if TEST_MODE:
        print(f"🧪 TEST MODE: Processing first {MAX_TEST_FILES} PDFs")
    print(f"Processing PDFs in: {MANUALS_DIR.absolute()}")
    print("=" * 60)
    print()

    # Get all PDF files
    pdf_files = sorted(MANUALS_DIR.glob("*.pdf"))

    if TEST_MODE:
        pdf_files = pdf_files[:MAX_TEST_FILES]

    if not pdf_files:
        print(f"❌ No PDF files found in {MANUALS_DIR}")
        return

    results = {}
    successful = 0
    failed = 0

    for idx, pdf_path in enumerate(pdf_files, 1):
        game_name = pdf_path.stem  # Filename without extension
        print(f"[{idx}/{len(pdf_files)}] {game_name}")

        code = extract_code_from_pdf(pdf_path)

        if code:
            results[game_name] = code
            successful += 1
            print(f"  ✅ Found: {code}")
        else:
            results[game_name] = None
            failed += 1
            print(f"  ❌ No code found")

        print()

    # Save results to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print("=" * 60)
    print("Summary:")
    print(f"  ✅ Codes found: {successful}")
    print(f"  ❌ Codes not found: {failed}")
    print(f"  📊 Success rate: {successful/len(pdf_files)*100:.1f}%")
    print(f"  💾 Results saved to: {OUTPUT_FILE.absolute()}")
    print("=" * 60)

    # Show some examples
    if successful > 0:
        print("\nSample codes found:")
        for i, (name, code) in enumerate(results.items()):
            if code and i < 5:
                print(f"  {name}: {code}")


if __name__ == "__main__":
    main()
