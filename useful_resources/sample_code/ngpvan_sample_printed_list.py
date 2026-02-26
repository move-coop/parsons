"""
****PLEASE NOTE: This script is NOT TESTED*****
This script pulls turf information (i.e. precinct name, list number, people count, door count, etc.)
from a specificed NGP VAN folder and creates a master check list and pdf printouts to circumvent
the sometimes lengthy process in VAN.
To use the script, be sure to set your environmental variables for VAN_API_KEY and
GOOGLE_DRIVE_CREDENTIALS.
The blog post explaining contextual information for this script can be found here: .
Please also note that due to the inability to test the script,
I decided to pare it down. It does not include turf prioritization, apartment demarcation,
and walkability scores as shown in the blog post.
To execute the script, run:
    python3 ngpvan_sample_printedlist.py \
    --van_folder_name="{Name of NGP VAN folder where printed lists are stored}" \
    --gsheet_uri="{URI for gsheet where NGP VAN data will be stored}"
"""

import click
from fpdf import FPDF

from parsons import VAN, GoogleSheets, Table

# ~~~~~~~~~~~~~~ Get Printed and Saved List Info From VAN ~~~~~~~~~~~~~~~~#


def get_info_from_van(van_folder):
    """
    Creates dataframe of relavent turf information in given folder

    Args:
        van_folder: str
            The name of the folder in NGP VAN where printed lists are stored

    Returns:
        dataframe

    """
    # Instantiate class
    van = VAN(db="MyVoters")

    # Get folder_id for inputed van_folder
    folders = van.get_folders().to_dataframe()
    folder_id = folders.folderId[folders.name == van_folder]

    # Get printed list number and turf/list name for all lists in van_folder
    printed_lists = van.get_printed_lists(folder_name=van_folder).to_dataframe()[["number", "name"]]

    # Get precinct name, turf door count, and turf people count for each turf in van_folder
    # by calling the saved_list methods
    saved_lists_raw = (
        van.get_saved_lists(folder_id=folder_id).to_dataframe().drop_duplicates(subset=["name"])
    )
    saved_lists = saved_lists_raw[saved_lists_raw.name.str.contains("Turf")]

    # Merge the printed list information with the saved list information into a single dataframe
    saved_printed_merged_raw = saved_lists[["name", "listCount", "doorCount"]].merge(
        printed_lists, on="name"
    )
    saved_printed_merged_renamed = saved_printed_merged_raw.rename(
        columns={
            "name": "Turf Name",
            "listCount": "Person Count",
            "doorCount": "Door Count",
            "number": "List Number",
        }
    )
    saved_printed_merged = saved_printed_merged_renamed.drop(columns=["name"])

    return saved_printed_merged


# ~~~~~~~~~~~~~~ Send master checklist to Google Sheets ~~~~~~~~~~~~~~~~#


def to_gsheet(saved_printed_merged, gsheet_uri):
    """
    Loads a dataframe into a gsheet
    Args:
        saved_printed_merged: df
            Info extracted from VAN from get_info_from_van function
        gsheet_uri: str
            URI for gsheet where dataframe info will be loaded
    Returns:
        None
    """
    # Instantiate GoogleSheet class
    sheets = GoogleSheets()

    # Send checklist info (i.e. saved_printed_merged dataframe) to google sheet
    sheets.overwrite_sheet(gsheet_uri, Table.from_dataframe(saved_printed_merged), worksheet="all")


# ~~~~~~~~~~~~~~ Generate pdf printouts ~~~~~~~~~~~~~~~~#


def to_pdf(saved_printed_merged):
    """
    Turns inputted dataframe into printable pdfs
    Args:
        saved_printed_merged: df
            Info extracted from VAN from get_info_from_van function
    Returns:
        None
    """
    pdf = FPDF()
    pdf.set_font("Arial", size=14)

    for _index, row in saved_printed_merged.iterrows():
        pdf.add_page()

        precinct_txt = f"Turf Name: {row[0]}"
        pdf.set_font_size(28)
        pdf.cell(w=200, h=15, txt=precinct_txt, ln=1, align="C")

        count_txt = f"People: {row[1]}    Doors: {row[2]}"
        pdf.set_font_size(23)
        pdf.cell(w=200, h=15, txt=count_txt, ln=1, align="C")

        list_txt = f"List Number: {row[3]}"
        pdf.set_font_size(19)
        pdf.cell(w=200, h=15, txt=list_txt, ln=1, align="C")

    pdf.output("printouts.pdf")


@click.command()
@click.option("--van_folder")
@click.option("--gsheet_uri")
def main(van_folder, gsheet_uri):
    """
    Loads turf data from NGP VAN to ghseet and creates PDF printouts
    Args:
        van_folder: str
            The name of the folder in NGP VAN where printed lists are stored
        gsheet_uri: str
            URI for gsheet where dataframe info will be loaded
    Returns:
        None
    """

    # gets turf-specific data from NGP VAN
    saved_printed_merged = get_info_from_van(van_folder)

    # loads data to specified gsheet
    to_gsheet(saved_printed_merged, gsheet_uri)

    # creates printable pdfs from NGP VAN data
    to_pdf(saved_printed_merged)


if __name__ == "__main__":
    main()
