import pymupdf
import json


doc = pymupdf.open("station-abbreviations.pdf")
codes = []
ignore_next = False

for page in doc[:-2]:
    tbl = page.find_tables(strategy="lines_strict")[0]
    for row in tbl.extract()[1:]:
        assert row[0] != ""
        assert any([(row[i] != "") for i in range(5)])
        
        # Edit station names.
        name = row[0].replace("\n", " ").replace(".", "").replace("By", "by").replace("Heathrow Airport Terminals 1,", "Heathrow Terminals")

        # Adjust for multiple entries.
        if ignore_next:
            ignore_next = False
            continue
        elif name[:12] == "Edgware Road":
            name = "Edgware Road"
            ignore_next = True
        elif name[:11] == "Hammersmith":
            name = "Hammersmith"
            ignore_next = True
        elif name[:10] == "Paddington":
            name = "Paddington"
            ignore_next = True

        codes.append({
            "name": name,
            "overground": row[1],
            "tramlink": row[2],
            "dlr": row[3],
            "underground": row[4]
        })
        
with open("data/codes.json", "w") as file:
    data = json.dumps(codes, indent=4)
    file.write(data)
