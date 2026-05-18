#this file takes ocr_output.json and generates two HTML reference sheets: one for Hydric Soil and one for Hydrology.
#each indicator label is wrapped in <b> tags; description text is plain.
#output is HTML suitable for pasting into Survey123 Connect XLSForm label cells.
#overwrite-safe: existing files in the output folder are replaced on each run.

from pathlib import Path
import json

#rename the XLSForm to {CURRENT_SURVEY}.xlsx
#type the name of the survey you are currently parsing (ie: great_plains, arid_west, etc.)
CURRENT_SURVEY = "great_plains"

REGION_NAME = "Great Plains"

INPUT_JSON = Path(f"output/{CURRENT_SURVEY}/ocr_output/ocr_output.json")
OUTPUT_FOLDER = Path(f"output/{CURRENT_SURVEY}/final_document")


#turns a name into a filename
def safe_filename(text):
    return text.lower().replace(" ", "_").replace("/", "_").replace("-", "_")


def escape_html(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_reference_sheet(category, indicators, part=None):
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    part_suffix = f"_part{part}" if part is not None else ""
    output_file = OUTPUT_FOLDER / f"{safe_filename(REGION_NAME)}_{safe_filename(category)}_reference_sheet{part_suffix}.html"

    part_label = f" - Part {part}" if part is not None else ""
    title = f"{REGION_NAME} - {category} Reference Sheet{part_label}"
    html_parts = [f"<h4>{escape_html(title)}</h4>"]

    for indicator in indicators:
        label = indicator.get("label", "").strip()
        raw_description = indicator.get("description", "").strip()

        #the OCR description always starts with a repeat of the label (sometimes
        #with slight OCR differences), so unconditionally strip the first line.
        desc_lines = raw_description.splitlines()
        if desc_lines:
            desc_lines = desc_lines[1:]
        description = "\n".join(desc_lines).strip()

        if not label:
            continue

        desc_html = escape_html(description if description else "No description provided.")
        #preserve line breaks from the source text
        desc_html = desc_html.replace("\n", "<br>")

        html_parts.append(f'<font size="2"><b>{escape_html(label)}</b><br>{desc_html}</font><br><br>')

    output_file.write_text("\n".join(html_parts), encoding="utf-8")
    print(f"Saved {category} sheet: {output_file}")


def main():
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Input JSON not found: {INPUT_JSON}")

    with open(INPUT_JSON, "r", encoding="utf-8") as file:
        data = json.load(file)

    wanted_categories = ["Hydric Soil", "Hydrology"]

    for category in wanted_categories:
        indicators = data.get(category, [])

        if not indicators:
            print(f"No indicators found for category: {category}")
            continue

        mid = len(indicators) // 2
        write_reference_sheet(category, indicators[:mid], part=1)                   #splits the output into two parts for two columns in the Survey123 entry
        write_reference_sheet(category, indicators[mid:], part=2)


if __name__ == "__main__":
    main()