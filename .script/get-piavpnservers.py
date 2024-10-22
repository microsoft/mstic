import requests
import json
import sys
import logging
import pandas as pd
from pathlib import Path


def download_pia_vpn_servers(output_file):

    new_data = []


    # V4
    logging.info(f"Downloading PIA VPN server list using API from https://serverlist.piaservers.net/vpninfo/servers/v4")


    r_v4 = requests.get("https://serverlist.piaservers.net/vpninfo/servers/v4")


    my_json_v4 = r_v4.content.decode("utf8")

    # Remove everything after the last brace
    my_json_v4 = my_json_v4[:my_json_v4.rfind('}')+1]


    data_v4 = json.loads(my_json_v4)["regions"]

    for region in data_v4:
        for protocol_type in region["servers"]:
            new_data.append({"ip": region["servers"][protocol_type][0]["ip"], "cn": region["servers"][protocol_type][0]["cn"], "id": region["id"],
                             "name": region["name"], "country": region["country"], "dns": region["dns"], "port_forward": str(region["port_forward"]), "protocol": protocol_type, "offline": ""})
            
    
    "----------------------------------------------------------------------------"


    # V5
    logging.info(f"Downloading PIA VPN server list using API from https://serverlist.piaservers.net/vpninfo/servers/v5")


    r_v5 = requests.get("https://serverlist.piaservers.net/vpninfo/servers/v5")


    my_json_v5 = r_v5.content.decode("utf8")

    # Remove everything after the last brace
    my_json_v5 = my_json_v5[:my_json_v5.rfind('}')+1]


    data_v5 = json.loads(my_json_v5)["regions"]

    for region in data_v5:
        for protocol_type in region["servers"]:
            new_data.append({"ip": region["servers"][protocol_type][0]["ip"], "cn": region["servers"][protocol_type][0]["cn"], "id": region["id"],
                             "name": region["name"], "country": region["country"], "dns": region["dns"], "port_forward": str(region["port_forward"]), "protocol": protocol_type, "offline": region["offline"] })
            
    
    "----------------------------------------------------------------------------"


    # V6
    logging.info(f"Downloading PIA VPN server list using API from https://serverlist.piaservers.net/vpninfo/servers/v6")


    r_v6 = requests.get("https://serverlist.piaservers.net/vpninfo/servers/v6")


    my_json_v6 = r_v6.content.decode("utf8")

    # Remove everything after the last brace
    my_json_v6 = my_json_v6[:my_json_v6.rfind('}')+1]

    data_v6 = json.loads(my_json_v6)["regions"]

    for region in data_v6:
        for protocol_type in region["servers"]:
            new_data.append({"ip": region["servers"][protocol_type][0]["ip"], "cn": region["servers"][protocol_type][0]["cn"], "id": region["id"],
                             "name": region["name"], "country": region["country"], "dns": region["dns"], "port_forward": str(region["port_forward"]), "protocol": protocol_type})


    df = pd.DataFrame(new_data)

    df.to_csv(output_file, index=False)



def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG,
        format="%(asctime)s:%(levelname)s: %(message)s",
    )
    logging.info("Python main function started")

    curr_path = Path.cwd()

    out_path = (
        curr_path / "master" / "PublicFeeds" / "PIAVPNDaily" / "pia-servers.csv"
    )
    try:
        out_path.parents[0].mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        logging.info("Folder is already present")
    else:
        logging.info(f"{out_path} Folder was created")

    logging.info(f"Writing csv file to output directory : {out_path}")
    download_pia_vpn_servers(out_path)


if __name__ == "__main__":
    main()
