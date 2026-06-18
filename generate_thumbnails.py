#!/usr/bin/env python3
"""
Generate thumbnail images from the first page of each PDF manual.
"""

import fitz  # PyMuPDF
from pathlib import Path
from PIL import Image

# Configuration
MANUALS_DIR = Path("./manuals")
THUMBNAILS_DIR = Path("./thumbnails")
THUMBNAIL_WIDTH = 300  # Width in pixels (height will be auto-scaled)
DPI = 150  # DPI for rendering (lower = faster, higher = better quality)
TEST_MODE = False  # Set to True to process only a few files
MAX_TEST_FILES = 5


def generate_thumbnail(pdf_path, output_path):
    """
    Generate a thumbnail image from the first page of a PDF.
    """
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)

        if len(doc) == 0:
            print(f"  ⚠️  No pages in PDF")
            return False

        # Get the first page
        page = doc[0]

        # Render the page to a pixmap
        mat = fitz.Matrix(DPI/72, DPI/72)  # Scale to DPI
        pix = page.get_pixmap(matrix=mat)

        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Resize to thumbnail width while maintaining aspect ratio
        aspect_ratio = img.height / img.width
        new_height = int(THUMBNAIL_WIDTH * aspect_ratio)
        img_resized = img.resize((THUMBNAIL_WIDTH, new_height), Image.Resampling.LANCZOS)

        # Save as JPEG (smaller file size than PNG)
        img_resized.save(output_path, "JPEG", quality=85, optimize=True)

        doc.close()
        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def main():
    """Generate thumbnails for all PDF manuals."""

    print("NES Manuals Thumbnail Generator")
    print("=" * 60)
    if TEST_MODE:
        print(f"🧪 TEST MODE: Processing first {MAX_TEST_FILES} PDFs")
    print(f"Input directory: {MANUALS_DIR.absolute()}")
    print(f"Output directory: {THUMBNAILS_DIR.absolute()}")
    print(f"Thumbnail size: {THUMBNAIL_WIDTH}px wide")
    print("=" * 60)
    print()

    # Create thumbnails directory
    THUMBNAILS_DIR.mkdir(exist_ok=True)

    # Get all PDF files
    pdf_files = sorted(MANUALS_DIR.glob("*.pdf"))

    if TEST_MODE:
        pdf_files = pdf_files[:MAX_TEST_FILES]

    if not pdf_files:
        print(f"❌ No PDF files found in {MANUALS_DIR}")
        return

    successful = 0
    failed = 0
    skipped = 0

    for idx, pdf_path in enumerate(pdf_files, 1):
        manual_name = pdf_path.stem  # Filename without extension
        output_filename = f"{manual_name}.jpg"
        output_path = THUMBNAILS_DIR / output_filename

        print(f"[{idx}/{len(pdf_files)}] {manual_name}")

        # Skip if thumbnail already exists
        if output_path.exists():
            print(f"  ⏭️  Already exists: {output_filename}")
            skipped += 1
            print()
            continue

        # Generate thumbnail
        if generate_thumbnail(pdf_path, output_path):
            file_size = output_path.stat().st_size / 1024  # KB
            print(f"  ✅ Created: {output_filename} ({file_size:.1f} KB)")
            successful += 1
        else:
            print(f"  ❌ Failed to create thumbnail")
            failed += 1

        print()

    # Summary
    print("=" * 60)
    print("Summary:")
    print(f"  ✅ Created: {successful}")
    print(f"  ⏭️  Skipped (already exist): {skipped}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📂 Thumbnails in: {THUMBNAILS_DIR.absolute()}")
    print("=" * 60)

    # Calculate total size
    if THUMBNAILS_DIR.exists():
        total_size = sum(f.stat().st_size for f in THUMBNAILS_DIR.glob("*.jpg")) / (1024 * 1024)  # MB
        print(f"\n📊 Total thumbnail size: {total_size:.1f} MB")


if __name__ == "__main__":
    main()
