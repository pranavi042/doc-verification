import re
import cv2
import numpy as np
import pytesseract
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.files.storage import default_storage
from pdf2image import convert_from_path
from .models import PanRecord, GstRecord, CinRecord



# -----------------------------
# COMMON OCR HELPERS
# -----------------------------

def read_image_from_file(path):
    """
    Supports both images and PDFs.
    """
    if path.lower().endswith(".pdf"):
        images = convert_from_path(path, dpi=300)
        if not images:
            return None
        img = np.array(images[0])
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img
    else:
        return cv2.imread(path)


def ocr_text(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return pytesseract.image_to_string(gray)


# -----------------------------
# PAN LOGIC
# -----------------------------

pan_pattern = r"[A-Z]{5}[0-9]{4}[A-Z]"


def extract_pan_details(text):
    text = text.upper()

    # PAN
    pan_match = re.search(pan_pattern, text)
    pan = pan_match.group() if pan_match else None

    # DOB
    dob_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    dob = dob_match.group() if dob_match else None

    # Name extraction
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    name = ""
    father_name = ""

    for i, line in enumerate(lines):
        if "INCOME TAX" in line:
            if i + 1 < len(lines):
                name = lines[i + 1]
            if i + 2 < len(lines):
                father_name = lines[i + 2]
            break

    return name, father_name, pan, dob


@api_view(["POST"])
def upload_pan(request):
    if "file" not in request.FILES:
        return Response({"status": "error", "message": "No file uploaded"})

    file = request.FILES["file"]
    path = default_storage.save(file.name, file)
    full_path = default_storage.path(path)

    img = read_image_from_file(full_path)
    if img is None:
        return Response({"status": "error", "message": "Invalid file"})

    text = ocr_text(img)

    name, father_name, pan, dob = extract_pan_details(text)

    if not pan:
        return Response({"status": "invalid", "message": "PAN not detected"})

    record, created = PanRecord.objects.get_or_create(
        pan_number=pan,
        defaults={
            "name": name,
            "father_name": father_name,
            "dob": dob,
        },
    )

    return Response(
        {
            "status": "registered",
            "data": {
                "name": record.name,
                "father_name": record.father_name,
                "pan": record.pan_number,
                "dob": record.dob,
            },
        }
    )


@api_view(["GET"])
def verify_pan(request, pan):
    try:
        record = PanRecord.objects.get(pan_number=pan)
        return Response(
            {
                "status": "verified",
                "data": {
                    "name": record.name,
                    "father_name": record.father_name,
                    "pan": record.pan_number,
                    "dob": record.dob,
                },
            }
        )
    except PanRecord.DoesNotExist:
        return Response({"status": "not_found"})


# -----------------------------
# GST LOGIC
# -----------------------------

gst_pattern = r"\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]"


def extract_gst_details(text):
    text = text.upper()
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    gst_pattern = r"\d{2}[A-Z]{5}\d{4}[A-Z]\d[Z][A-Z0-9]"
    gst_match = re.search(gst_pattern, text)
    gst = gst_match.group() if gst_match else None

    def get_value_after(label):
        for i, line in enumerate(lines):
            if label in line:
                # try same line after colon
                parts = line.split(":")
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip()

                # otherwise next line
                if i + 1 < len(lines):
                    return lines[i + 1]
        return ""

    details = {
        "registration_number": get_value_after("REGISTRATION NUMBER"),
        "legal_name": get_value_after("LEGAL NAME"),
        "trade_name": get_value_after("TRADE NAME"),
        "additional_trade_name": get_value_after("ADDITIONAL TRADE NAME"),
        "constitution": get_value_after("CONSTITUTION"),
        "address": get_value_after("ADDRESS"),
        "date_of_liability": get_value_after("DATE OF LIABILITY"),
        "date_of_registration": get_value_after("DATE OF REGISTRATION"),
        "period_of_validity": get_value_after("VALIDITY"),
        "type_of_registration": get_value_after("TYPE OF REGISTRATION"),
        "approving_authority": get_value_after("APPROVING"),
        "designation": get_value_after("DESIGNATION"),
        "jurisdiction": get_value_after("JURISDICTION"),
        "date_of_issue": get_value_after("DATE OF ISSUE"),
    }

    return details, gst

@api_view(["POST"])
def upload_gst(request):
    if "file" not in request.FILES:
        return Response({"status": "error", "message": "No file uploaded"})

    file = request.FILES["file"]
    path = default_storage.save(file.name, file)
    full_path = default_storage.path(path)

    img = read_image_from_file(full_path)
    if img is None:
        return Response({"status": "error", "message": "Invalid file"})

    text = ocr_text(img)

    details, gst = extract_gst_details(text)

    if not gst:
        return Response({"status": "invalid", "message": "GST not detected"})

    record, created = GstRecord.objects.get_or_create(
        gst_number=gst,
        defaults={
            "legal_name": details["legal_name"],
            "trade_name": details["trade_name"],
        },
    )

    return Response(
        {
            "status": "registered",
            "data": {
                "registration_number": details["registration_number"],
                "legal_name": details["legal_name"],
                "trade_name": details["trade_name"],
                "additional_trade_name": details["additional_trade_name"],
                "constitution": details["constitution"],
                "address": details["address"],
                "date_of_liability": details["date_of_liability"],
                "date_of_registration": details["date_of_registration"],
                "period_of_validity": details["period_of_validity"],
                "type_of_registration": details["type_of_registration"],
                "approving_authority": details["approving_authority"],
                "designation": details["designation"],
                "jurisdiction": details["jurisdiction"],
                "date_of_issue": details["date_of_issue"],
                "gst": gst,
            },
        }
    )




@api_view(["GET"])
def verify_gst(request, gst):
    try:
        record = GstRecord.objects.get(gst_number=gst)
        return Response(
            {
                "status": "verified",
                "data": {
                    "legal_name": record.legal_name,
                    "trade_name": record.trade_name,
                    "gst": record.gst_number,
                },
            }
        )
    except GstRecord.DoesNotExist:
        return Response({"status": "not_found"})

# CIN pattern (example: U12345MH2020PTC123456)
cin_pattern = r"[A-Z]{1}[0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}"

def extract_cin_details(text):
    text = text.upper()

    # Extract CIN number
    cin_match = re.search(cin_pattern, text)
    cin = cin_match.group() if cin_match else None

    # Extract company name
    company_name = ""
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    for line in lines:
        if "LIMITED" in line or "PRIVATE" in line:
            company_name = line
            break

    # Extract registration date
    date_match = re.search(r"\d{2}/\d{2}/\d{4}", text)
    registration_date = date_match.group() if date_match else ""

    return company_name, registration_date, cin

@api_view(["POST"])
def upload_cin(request):
    if "file" not in request.FILES:
        return Response({"status": "error", "message": "No file uploaded"})

    file = request.FILES["file"]
    path = default_storage.save(file.name, file)
    full_path = default_storage.path(path)

    img = read_image_from_file(full_path)
    if img is None:
        return Response({"status": "error", "message": "Invalid file"})

    text = ocr_text(img)
    print("CIN OCR TEXT:")
    print(text)


    company_name, registration_date, cin = extract_cin_details(text)

    if not cin:
        return Response({"status": "invalid", "message": "CIN not detected"})

    record, created = CinRecord.objects.get_or_create(
        cin_number=cin,
        defaults={
            "company_name": company_name,
            "registration_date": registration_date,
        },
    )

    return Response(
        {
            "status": "registered",
            "data": {
                "cin": record.cin_number,
                "company_name": record.company_name,
                "registration_date": record.registration_date,
            },
        }
    )

@api_view(["GET"])
def verify_cin(request, cin):
    try:
        record = CinRecord.objects.get(cin_number=cin)
        return Response(
            {
                "status": "verified",
                "data": {
                    "cin": record.cin_number,
                    "company_name": record.company_name,
                    "registration_date": record.registration_date,
                },
            }
        )
    except CinRecord.DoesNotExist:
        return Response({"status": "not_found"})
