"""Create the publication copy of the Phase 2 workbook by patching ONE worksheet part of the zip.
Only MARKET FRAMEWORK display formulas change: when required inputs are missing they show "Not calculated"
instead of 0. Every other part of the package (all scenario sheets, the chart, styles) is copied byte for byte.
The original workbook is read only. Output: publication/Pilot_ROI_and_Venture_Model_PUBLICATION_COPY.xlsx"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "Pilot_ROI_and_Venture_Model.xlsx"
OUT = ROOT / "publication" / "Pilot_ROI_and_Venture_Model_PUBLICATION_COPY.xlsx"
SHEET = "xl/worksheets/sheet10.xml"  # MARKET FRAMEWORK (sheetId 10)

OLD12 = '<x:c r="D12" s="36" t="n"><x:f>IF(COUNT(D9:D11)=3,D9*D10*D11,0)</x:f><x:v>0</x:v></x:c>'
NEW12 = '<x:c r="D12" s="36" t="str"><x:f>IF(COUNT(D9:D11)=3,D9*D10*D11,"Not calculated")</x:f><x:v>Not calculated</x:v></x:c>'
OLD14 = '<x:c r="D14" s="36" t="n"><x:f>IF(COUNT(D12:D13)=2,D12*D13,0)</x:f><x:v>0</x:v></x:c>'
NEW14 = '<x:c r="D14" s="36" t="str"><x:f>IF(COUNT(D12:D13)=2,D12*D13,"Not calculated")</x:f><x:v>Not calculated</x:v></x:c>'
NOTE = ('<x:row r="21"><x:c r="A21" t="inlineStr"><x:is><x:t>PUBLICATION COPY. Only the two market-size display formulas above were changed '
        '(missing inputs show "Not calculated" instead of 0). All other sheets are identical to Pilot_ROI_and_Venture_Model.xlsx, '
        'which remains the original. No market size is estimated here.</x:t></x:is></x:c></x:row>')


def main() -> None:
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == SHEET:
                s = data.decode("utf-8")
                for old, new in ((OLD12, NEW12), (OLD14, NEW14)):
                    if s.count(old) != 1:
                        sys.exit(f"expected cell XML not found: {old[:40]}")
                    s = s.replace(old, new)
                if "</x:sheetData>" not in s or 'r="21"' in s:
                    sys.exit("unexpected sheet layout")
                s = s.replace("</x:sheetData>", NOTE + "</x:sheetData>", 1)
                data = s.encode("utf-8")
            zout.writestr(item, data)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
