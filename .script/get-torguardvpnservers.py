import sys
import logging
import json
import pandas as pd
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
from pathlib import Path


def json_flip_to_list(old_json):
    new_list = []
    for key in old_json:
        for val in old_json[key]:
            new_list.append({"ip_address": val, "domain": key})
    return new_list


def download_torguardvpn_vpn_servers(url, dns_file_name, output_file):
        zip_file = urlopen(url)
        archive = ZipFile(BytesIO(zip_file.read()))
        my_json = archive.read(dns_file_name).decode("utf8")
        json_data = json.loads(my_json)
        list_data = json_flip_to_list(json_data["resolve"])
        df = pd.DataFrame(list_data)
        # Convert to csv
        df.to_csv(output_file, index=False)


def main():

    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s: %(message)s",
    )

    dns_file_name = "dns.json"
    zip_url = "https://updates.torguard.biz/prod/Config/default.zip"

    logging.info(f"Downloading Tor TorGuard server list using dns config file from {zip_url}")

    curr_path = Path.cwd()
    out_path = (
        curr_path / "master" / "PublicFeeds" / "TorGuardVPNDaily" / "torguardvpn-servers.csv"
    )

    try:
        out_path.parents[0].mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logging.info("Folder is already present")
    else:
        logging.info(f"{out_path} Folder was created")

    logging.info(f"Writing csv file to output directory : {out_path}")

    download_torguardvpn_vpn_servers(zip_url, dns_file_name, out_path)


if __name__ == "__main__":
    main()
