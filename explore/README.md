# API Probe Tool

This tool sequentially probes the Sigma Labs Plant API and saves each successful response as a formatted JSON file.

## Usage

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```



2. **Run the tool:**

   To probe a range of IDs:
   ```bash
   python main.py -count 100
   ```
   Replace `100` with the maximum plant ID you want to probe (inclusive).

   To probe specific IDs:
   ```bash
   python main.py -ids 1 5 8 13
   ```
   List the IDs you want to probe, separated by spaces.

   Optionally, specify an output directory (default is `output`):
   ```bash
   python main.py -count 100 -output myfolder
   python main.py -ids 1 5 8 13 -output myfolder
   ```

3. **Output:**

   - For each successful API response, a file named `0000_name.json`, `0001_name.json`, etc., will be created in the specified output directory (default: `output`).
   - The `name` in the filename is taken from the API response's `name` attribute.

## Notes
- Requires Python 3.6 or higher.
- Each request is performed sequentially.
- Only successful responses (HTTP 200) are saved.
