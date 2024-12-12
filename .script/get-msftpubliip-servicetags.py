import requests
import json
import logging
import sys
import json
import pandas as pd
from pathlib import Path
from requests_html import HTMLSession


def parse_and_download_files(servicetags_public, msftpublic_ips, officeworldwide_ips):
    # URL for Feeds
    azurepublic = "https://www.microsoft.com/en-us/download/details.aspx?id=56519"
    msftpublic = "https://www.microsoft.com/en-us/download/details.aspx?id=53602"
    officeworldwide = "https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7"

    session = HTMLSession()
    azure_resp = session.get(azurepublic)
    links = azure_resp.html.links
    json_link = [link for link in links if ".json" in link]

    msft_resp = session.get(msftpublic)
    links = msft_resp.html.links
    csv_link = [link for link in links if ".csv" in link]

    # Download JSON link
    azure_json = requests.get(json_link[0])
    msft_csv = requests.get(csv_link[0], stream=True)
    o365_json = requests.get(officeworldwide, stream=True)
    # Write output file
    logging.info("Writing ServiceTags_Public.json file to output directory")
    with open(servicetags_public, "w") as f:
        json.dump(azure_json.json(), f, indent=4)
    logging.info("Writing MSFT_PublicIPs.csv file to output directory")
    with open(msftpublic_ips, "wb") as f:
        for line in msft_csv.iter_lines():
            f.write(line + "\n".encode())
    logging.info("Writing OfficeWorldWide-IPRanges.json file to output directory")
    with open(officeworldwide_ips, "w") as f:
        json.dump(o365_json.json(), f, indent=4)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s: %(message)s",
    )

    curr_path = Path.cwd()
    out_path = curr_path / "master" / "PublicFeeds" / "MSFTIPRanges"
    try:
        out_path.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logging.info("Folder is already present")
    else:
        logging.info(f"{out_path} Folder was created")

    servicetags_public = (
        curr_path
        / "master"
        / "PublicFeeds"
        / "MSFTIPRanges"
        / "ServiceTags_Public.json"
    )
    msftpublic_ips = (
        curr_path / "master" / "PublicFeeds" / "MSFTIPRanges" / "MSFT_PublicIPs.csv"
    )
    officeworldwide_ips = (
        curr_path
        / "master"
        / "PublicFeeds"
        / "MSFTIPRanges"
        / "OfficeWorldWide-IPRanges.json"
    )

    logging.info(f"Writing json file to output directory : {servicetags_public}")
    logging.info(f"Writing csv file to output directory : {msftpublic_ips}")
    logging.info(f"Writing json file to output directory : {officeworldwide_ips}")
    parse_and_download_files(servicetags_public, msftpublic_ips, officeworldwide_ips)


if __name__ == "__main__":
    main()
