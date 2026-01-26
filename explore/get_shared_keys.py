import os
import json


def get_shared_and_nonshared_keys(directory):
    shared_keys = None
    all_keys = set()
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            path = os.path.join(directory, filename)
            with open(path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, dict):
                        keys = set(data.keys())
                        all_keys |= keys
                        if shared_keys is None:
                            shared_keys = keys
                        else:
                            shared_keys &= keys
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
    if shared_keys is None:
        shared_keys = set()
    non_shared_keys = all_keys - shared_keys
    return shared_keys, non_shared_keys


if __name__ == '__main__':
    output_dir = 'output'
    shared, non_shared = get_shared_and_nonshared_keys(output_dir)
    print(f"Shared keys across all JSON files in '{output_dir}':")
    for k in sorted(shared):
        print(k)
    print("\nNon-shared keys (present in some but not all files):")
    for k in sorted(non_shared):
        print(k)
