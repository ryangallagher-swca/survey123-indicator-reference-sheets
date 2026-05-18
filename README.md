# Survey123 Indicator Reference Sheets

Generates HTML reference sheets for wetland delineation indicator images extracted from Survey123 XLSForm surveys. The pipeline reads indicator choices from an XLSForm, copies the associated images, runs OCR on each one, and produces HTML output ready to paste into Survey123 Connect label cells.

---

## Requirements

**Python 3.8+**

Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies:
- `openpyxl` — reads the XLSForm (.xlsx)
- `easyocr` — extracts text from indicator images

> EasyOCR will download its English language model on first run (~100 MB).

---

## Input Data

Each survey lives under `data/{CURRENT_SURVEY}/` and requires:

```
data/
└── {CURRENT_SURVEY}/
    ├── xlsform/
    │   └── {CURRENT_SURVEY}.xlsx   ← the Survey123 XLSForm
    └── media/
        └── *.jpg                   ← all indicator images referenced by the XLSForm
```

Rename your XLSForm to match the survey name (e.g., `great_plains.xlsx`) and set `CURRENT_SURVEY` at the top of each script before running.

---

## Pipeline

Run the scripts in order:

### 1. `extract_choices_to_json.py`

Reads the `choices` sheet of the XLSForm and extracts all Hydric Soil and Hydrology indicator entries (label, list name, image filename) into a mapping JSON.

**Output:** `output/{CURRENT_SURVEY}/review/{CURRENT_SURVEY}_indicator_mapping.json`

---

### 2. `copy_referenced_images.py`

Uses the mapping JSON to copy each indicator's image from `data/{CURRENT_SURVEY}/media/` into the output folder, organized by category.

**Output:**
- `output/{CURRENT_SURVEY}/referenced_images/hydric_soil/`
- `output/{CURRENT_SURVEY}/referenced_images/hydrology/`
- `output/{CURRENT_SURVEY}/referenced_images/missing_files.json` ← any images not found

---

### 3. `ocr_images.py`

Runs EasyOCR on each copied image to extract the description text printed on the indicator card.

**Output:** `output/{CURRENT_SURVEY}/ocr_output/ocr_output.json`

> You can manually edit the `description` values in this file to fix any OCR errors before proceeding to the next step.

---

### 4. `generate_reference_sheets.py`

Reads `ocr_output.json` and generates HTML reference sheets for Hydric Soil and Hydrology, split into two parts each.

**Output:** `output/{CURRENT_SURVEY}/final_document/*.html`

The HTML files are formatted for pasting directly into Survey123 Connect XLSForm label cells.

---

## Output Structure

```
output/
└── {CURRENT_SURVEY}/
    ├── review/
    │   └── {CURRENT_SURVEY}_indicator_mapping.json
    ├── ocr_output/
    │   └── ocr_output.json
    ├── referenced_images/
    │   ├── hydric_soil/
    │   ├── hydrology/
    │   └── missing_files.json
    └── final_document/
        ├── {region}_hydric_soil_reference_sheet_part1.html
        ├── {region}_hydric_soil_reference_sheet_part2.html
        ├── {region}_hydrology_reference_sheet_part1.html
        └── {region}_hydrology_reference_sheet_part2.html
```

---

## Adding a New Survey

1. Place the XLSForm at `data/{survey_name}/xlsform/{survey_name}.xlsx`
2. Place all media images at `data/{survey_name}/media/`
3. Set `CURRENT_SURVEY = "{survey_name}"` (and `REGION_NAME` in `generate_reference_sheets.py`) in each script
4. Run the pipeline steps in order
