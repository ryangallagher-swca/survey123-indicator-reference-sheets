#This file takes the json output from extract_choices_to_json.py, gets the filenames associated with each indicator, and copies each file over from the media folder into the designated output folder at output/great_plains/reference_sheets/great_plains_reference_images
#File paths will be changed depending on which survey we are working with 

from pathlib import Path
import json
import shutil

#Rename the XLSForm to {CURRENT_SURVEY}.xlsx
#Type the name of the survey you are currently parsing (ie: great_plains, arid_west, etc.)
CURRENT_SURVEY = "great_plains"

MAPPING_JSON = Path(f"output/{CURRENT_SURVEY}/review/{CURRENT_SURVEY}_indicator_mapping.json")
MEDIA_FOLDER = Path(f"data/{CURRENT_SURVEY}/media")
OUTPUT_FOLDER = Path(f"output/{CURRENT_SURVEY}/referenced_images")

#makes category names folder names
def safe_folder_name(name):
    return name.lower().replace(" ", "_")

def main():
    if not MAPPING_JSON.exists():
        raise FileNotFoundError(f"Mapping JSON not found: {MAPPING_JSON}")
    
    if not MEDIA_FOLDER.exists():
        raise FileNotFoundError(f"Media folder not found: {MEDIA_FOLDER}")
    
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)                                         #ensures that the output folder exists

    with open(MAPPING_JSON, "r", encoding="utf-8") as file:
        indicator_data = json.load(file)                                                        #indicator_data now is the dictionary of the XLSForm rows


    copied_count = 0
    missing_count = 0
    missing_files = []

    for category, indicators in indicator_data.items():                                     #.items() basically gives you a list of 2 element tuples
        category_folder = OUTPUT_FOLDER / safe_folder_name(category)                        #makes the path for the category folder
        category_folder.mkdir(parents=True, exist_ok=True)

        for indicator in indicators:
            label = indicator.get("label", "")
            image_filename = indicator.get("image_filename", "")

            if label == "Other (Explain in Remarks)":                                       #no file attached to it
                continue

            if not image_filename:
                print(f"No image filename for: {label}")
                missing_count += 1
                missing_files.append({
                    "label": label,
                    "image_filename": image_filename,
                    "reason": "No filename is in XLSForm"
                })
                continue

            source_path =  MEDIA_FOLDER / image_filename
            destination_path = category_folder / image_filename

            if source_path.exists():
                shutil.copy2(source_path, destination_path)                                     #copies the desired file from the media folder to the output folder
                copied_count += 1
            else: 
                print(f"Missing file: {source_path}")
                missing_count += 1
                missing_files.append({
                    "label": label,
                    "image_filename": image_filename,
                    "reason": "File not found in media folder"
                })

    missing_report = OUTPUT_FOLDER / "missing_files.json"
    with open(missing_report, "w", encoding="utf-8") as file:
        json.dump(missing_files, file, indent=2, ensure_ascii=False)

    
    print(f"Copied files: {copied_count}")
    print(f"Missing files: {missing_count}")
    print(f"Copied images saved to: {OUTPUT_FOLDER}")
    print(f"Missing file report saved to: {missing_report}")



if __name__ == "__main__":
    main()
