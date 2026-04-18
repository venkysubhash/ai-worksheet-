# ==========================================================
# CAIGS ULTRA AI - PDF ENGINE (STABLE + CLEAN)
# ==========================================================

import fitz  # PyMuPDF
import os
import pytesseract
import cv2
import uuid
from PIL import Image as PILImage
import numpy as np
import hashlib

# ==========================================================
# SAFE OCR FUNCTION
# ==========================================================

def ocr_image(image_path):

    try:
        img = cv2.imread(image_path)

        if img is None:
            return ""

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Optional noise reduction
        gray = cv2.medianBlur(gray, 3)

        text = pytesseract.image_to_string(gray)

        if text:
            return text.strip()

        return ""

    except Exception:
        return ""


# ==========================================================
# IMAGE SAVE HELPER
# ==========================================================

def save_image_bytes(image_bytes, extension):

    os.makedirs("static/generated", exist_ok=True)

    unique_name = f"img_{uuid.uuid4().hex}.{extension}"
    image_path = os.path.join("static/generated", unique_name)

    try:
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        return image_path
    except Exception:
        return None


# ==========================================================
# CLEAN TEXT BLOCK
# ==========================================================

def clean_page_text(text):

    if not text:
        return ""

    # Remove excessive whitespace
    text = " ".join(text.split())

    # Remove standalone numbers
    import re
    text = re.sub(r"\b\d+\b", "", text)

    return text.strip()

def is_valid_image(path):
    try:
        img = PILImage.open(path).convert("L")
        arr = np.array(img)

        # Remove mostly black images
        if arr.mean() < 15:
            return False

        # Remove very small images (icons/masks)
        if img.width < 80 or img.height < 80:
            return False

        return True
    except:
        return False
# ==========================================================
# MAIN EXTRACTION FUNCTION
# ==========================================================

def extract_text_and_images_from_pdf(file_path):

    if not os.path.exists(file_path):
        return "", []

    try:
        doc = fitz.open(file_path)
    except Exception:
        return "", []

    full_text = []
    image_paths = []

    for page_index in range(len(doc)):

        try:
            page = doc[page_index]
        except Exception:
            continue

        # --------------------------------------------------
        # TEXT EXTRACTION
        # --------------------------------------------------

        try:
            page_text = page.get_text("text")
            page_text = clean_page_text(page_text)

            if page_text and len(page_text.split()) > 5:
                full_text.append(page_text)

        except Exception:
            pass

        # --------------------------------------------------
        # IMAGE EXTRACTION
        # --------------------------------------------------

        try:
            images = page.get_images(full=True)
        except Exception:
            images = []

        for img in images:

            try:
                xref = img[0]
                base_image = doc.extract_image(xref)

                image_bytes = base_image.get("image", None)
                image_ext = base_image.get("ext", "png")

                if not image_bytes:
                    continue

                image_path = save_image_bytes(image_bytes, image_ext)

                if not image_path:
                    continue

                if is_valid_image(image_path):
                    image_paths.append(image_path)
                else:
                    os.remove(image_path)
                    continue


                # --------------------------------------------------
                # SAFE OCR (ONLY ON VALID FORMATS)
                # --------------------------------------------------

                if image_ext.lower() in ["png", "jpg", "jpeg"]:

                    ocr_text = ocr_image(image_path)

                    if ocr_text and len(ocr_text.split()) > 5:
                        full_text.append(ocr_text)

            except Exception:
                continue

    doc.close()

    # ------------------------------------------------------
    # FINAL CLEAN TEXT JOIN
    # ------------------------------------------------------

    combined_text = "\n".join(full_text)

    # Remove duplicated lines
    lines = combined_text.split("\n")
    unique_lines = []

    seen = set()

    for line in lines:
        stripped = line.strip()

        if stripped and stripped not in seen:
            unique_lines.append(stripped)
            seen.add(stripped)

    final_text = "\n".join(unique_lines)
    # Remove duplicate images by content hash
    unique_hashes = {}
    clean_images = []

    for img_path in image_paths:
        try:
            with open(img_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            if file_hash not in unique_hashes:
                unique_hashes[file_hash] = True
                clean_images.append(img_path)
            else:
                os.remove(img_path)
        except:
            continue

    image_paths = clean_images
    return final_text.strip(), image_paths