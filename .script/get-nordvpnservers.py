import requests
import json
import sys
import logging
import pandas as pd
from pathlib import Path

"https://api.nordvpn.com/server"


def download_nord_vpn_servers(url, output_file):
    # Download data from the url
    r = requests.get(url)

    # Decode byte array into string
    my_json = r.content.decode("utf8")

    # Convert string to JSON
    data = json.loads(my_json)

    # Load list of JSON records into dataframe
    df = pd.DataFrame(data)
    # Convert to csv
    df.to_csv(output_file, index=False)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s: %(message)s",
    )
    api_url = "https://api.nordvpn.com/v1/servers"
    logging.info("Python main function started")
    logging.info(f"Downloading Nord VPN server list using API from {api_url}")

    curr_path = Path.cwd()
    out_path = (
        curr_path / "master" / "PublicFeeds" / "NordVPNDaily" / "nordvpn-servers.json"
    )
    try:
        out_path.parents[0].mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logging.info("Folder is already present")
    else:
        logging.info(f"{out_path} Folder was created")

    logging.info(f"Writing JSON file to output directory : {out_path}")
    download_nord_vpn_servers(api_url, out_path)


if __name__ == "__main__":
    main()
