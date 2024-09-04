import pandas as pd
import xml.etree.ElementTree as ET
from collections import defaultdict


def palms_to_df(filename: str) -> pd.DataFrame:
    """
    Converts a PALMS XML file to a pandas DataFrame.

    Args:
        filename (str): Path to the PALMS XML file.

    Returns:
        pd.DataFrame: DataFrame containing the data from the PALMS XML file.
    """
    tree = ET.parse(filename)
    root = tree.getroot()

    xml_rows = []
    for l1 in root:
        if l1.tag.endswith("Worksheet"):
            for l2 in l1:
                if l2.tag.endswith("Table"):
                    for l3 in l2:
                        if l3.tag.endswith("Row"):
                            row = []
                            for l4 in l3:
                                if l4.tag.endswith("Cell"):
                                    for l5 in l4:
                                        if l5.tag.endswith("Data"):
                                            row.append(str(l5.text))
                            xml_rows.append(row)

    for i, (row0, row1) in enumerate(zip(xml_rows, xml_rows[1:])):
        if not isinstance(row0, list):
            raise ValueError("Expected row to be a list")

        if str(row0[0]).lower().startswith("running user"):
            metadata = dict(
                zip(
                    map(lambda x: str(x).strip(), row0),
                    map(lambda x: str(x).strip(), row1),
                )
            )
            break

    for j, row in enumerate(xml_rows[i + 2 :], start=i + 2):
        if not isinstance(row, list):
            raise ValueError("Expected row to be a list")

        if str(row[0]).lower().lstrip().startswith("first name"):
            break

        if len(row) > 1 and str(row[1]).strip():
            metadata[str(row[0]).replace(":", "").strip()] = str(row[1]).strip()

        if isinstance(row, list) and str(row[0]).lower().startswith("running user"):
            xml_rows.remove(row)
            break

    header_row = tuple(map(lambda x: str(x).strip(), xml_rows[j]))
    df_data = defaultdict(list)

    for row in xml_rows[(j + 1) :]:
        if not isinstance(row, list):
            raise ValueError("Expected row to be a list")

        for k, v in zip(header_row, map(lambda x: str(x).strip(), row)):
            df_data[k].append(v)

    ds = pd.Series(
        {
            "Country": metadata.get("Country", None),
            "Region": metadata.get("Region", None),
            "Chapter": metadata.get("Chapter", None),
            "From": metadata.get("From", None),
            "To": metadata.get("To", None),
            "Run At": metadata.get("Run At", None),
            "Flags": metadata.get("Flags", None),
        }
    )

    df = pd.DataFrame(df_data)

    df = pd.concat(
        [
            df,
            pd.concat([ds] * len(df), axis=1).T.reset_index(drop=True),
        ],
        axis=1,
    )

    return df


filename = "data/palms.xml"
print(palms_to_df(filename).head())
