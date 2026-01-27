"""Script to probe an API for plant data and save responses as JSON files."""

import json
import os
import argparse
import requests


def probe_api(ids, output_dir):
    """Probe the API for given IDs and save responses as JSON files."""
    url_template = 'https://tools.sigmalabs.co.uk/api/plants/{}'
    os.makedirs(output_dir, exist_ok=True)
    for i in ids:
        url = url_template.format(i)
        try:
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                name = data.get('name', f'no_name_{i}')
                safe_name = str(name).replace(' ', '_').replace('/', '_')
                filename = os.path.join(
                    output_dir, f"{i:04d}_{safe_name}.json")
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f"Saved: {filename}")
            else:
                err_msg = resp.text.strip()
                print(f"ID {i}: Status {resp.status_code} - {err_msg}")
        except Exception as e:
            print(f"ID {i}: Error {e}")


def main():
    """Create the argument parser and initiate the API probing."""
    parser = argparse.ArgumentParser(description='Sequential API probe tool')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-count', type=int, help='Max ID to probe (inclusive)')
    group.add_argument('-ids', nargs='+', type=int,
                       help='List of specific IDs to probe (space separated)')
    parser.add_argument('-output', type=str, default='output',
                        help='Output directory for JSON files (default: output)')
    args = parser.parse_args()

    if args.ids is not None:
        ids = args.ids
    else:
        ids = list(range(args.count + 1))
    probe_api(ids, args.output)


if __name__ == '__main__':
    main()
