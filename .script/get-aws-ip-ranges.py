import requests
import json
import sys
import logging
from pathlib import Path

def download_aws_ip_ranges(url, output_file):
    response = requests.get(url)
    response.raise_for_status()  # Raise error for bad response
    data = response.json()
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s"
    )

    aws_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    logging.info(f"Downloading AWS IP ranges from {aws_url}")

    out_path = Path("master") / "PublicFeeds" / "AWSIPRanges" / "aws-ip-ranges.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    download_aws_ip_ranges(aws_url, out_path)
    logging.info(f"AWS IP ranges saved to {out_path}")

if __name__ == "__main__":
    main()
