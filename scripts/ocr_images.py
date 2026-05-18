#This file goes through the indicator_mapping created from extract_choices_to_json.py, reads the image_filename and associated label of each entry, easyocr then scans each photo and outputs the description text from each one to output/{CURRENT_SURVEY}/ocr_output/ocr_output.json with Hydric Soil Indicators and Hydrology the two keys in the dictionary, values being the list of dictionaries with information about each indicator
from pathlib import Path
import json
import warnings
import easyocr

#Rename the XLSForm to {CURRENT_SURVEY}.xlsx
#Type the name of the survey you are currently parsing (ie: great_plains, arid_west, etc.)
CURRENT_SURVEY = "great_plains"

MAPPING_JSON = Path(f"output/{CURRENT_SURVEY}/review/{CURRENT_SURVEY}_indicator_mapping.json")
REFERENCED_IMAGES_FOLDER = Path(f"output/{CURRENT_SURVEY}/referenced_images")

OUTPUT_JSON = Path(f"output/{CURRENT_SURVEY}/ocr_output/ocr_output.json")


#runs easyocr in explicit cpu mode so we do not get warnings
warnings.filterwarnings(
    "ignore",
    message="'pin_memory' argument is set as true but no accelerator is found, then device pinned memory won't be used.",
    category=UserWarning,
    module=r"torch\.utils\.data\.dataloader",
)


#makes the category names folder names
def safe_folder_name(name):
    return name.lower().replace(" ", "_")


def is_supported_image_file(path: Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}


#cleans the retuend list of strings into one string
def clean_ocr_result(ocr_result):
    cleaned_lines = []

    for line in ocr_result:
        line = str(line).strip()
        if line:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

def main():
    if not MAPPING_JSON.exists():
        raise FileNotFoundError(f"Mapping JSON not found: {MAPPING_JSON}")
    
    with open(MAPPING_JSON, "r", encoding="utf-8") as file:
        indicator_data = json.load(file)

    reader = easyocr.Reader(["en"], gpu=False, verbose=False)

    ocr_output = {}

    for category, indicators in indicator_data.items():
        ocr_output[category] = []

        category_folder = REFERENCED_IMAGES_FOLDER / safe_folder_name(category)

        for indicator in indicators:
            label = indicator.get("label")
            image_filename = indicator.get("image_filename")

            if not image_filename:
                print(f"Missing image filename for {label}")

                ocr_output[category].append({
                    "label": label,
                    "image_filename": image_filename,
                    "description": "",
                    "status": "missing image filename"
                })

                continue

            image_path = category_folder / image_filename

            if image_path.is_dir() or not is_supported_image_file(image_path):
                print(f"Skipping non-image path for {label}: {image_path}")

                ocr_output[category].append({
                    "label": label,
                    "image_filename": image_filename,
                    "description": "",
                    "status": "non-image path"
                })

                continue

            if not image_path.exists():
                print(f"Missing image for {label}: {image_path}")

                ocr_output[category].append({
                    "label": label,
                    "image_filename": image_filename,
                    "description": "",
                    "status": "missing image"
                })

                continue

            
            
            result = reader.readtext(str(image_path), detail=0)                                             #reads the image text and returns a list of strings
            raw_text = clean_ocr_result(result)

            ocr_output[category].append({
                    "label": label,
                    "image_filename": image_filename,
                    "description": raw_text,
                    "status": "ocr complete"
                })
            
        
        print(f"OCR complete for: {category}")


    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as file:
        json.dump(ocr_output, file, indent=2, ensure_ascii=False)

    print(f"Saved OCR output to {OUTPUT_JSON}")




if __name__ == "__main__":
    main()

