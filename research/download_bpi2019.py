import os
import requests
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEST_DIR = os.path.join(BASE_DIR, "original_datasets", "procurement_expenses", "bpi_2019")
os.makedirs(DEST_DIR, exist_ok=True)

url = "http://icpmconference.org/2019/wp-content/uploads/sites/6/2019/02/BPIChallenge2019CSV.zip"
zip_path = os.path.join(DEST_DIR, "BPIChallenge2019CSV.zip")

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

print(f"Connecting to: {url}...")
try:
    resp = requests.get(url, headers=headers, stream=True, timeout=30)
    print("HTTP Status:", resp.status_code)
    if resp.status_code == 200:
        total_len = resp.headers.get('content-length')
        if total_len:
            total_len = int(total_len)
            print(f"Total size: {total_len:,} bytes ({total_len / 1024 / 1024:.2f} MB)")
        
        downloaded = 0
        with open(zip_path, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_len:
                        pct = (downloaded / total_len) * 100
                        print(f"Downloaded {downloaded:,} / {total_len:,} bytes ({pct:.1f}%)...")
                    else:
                        print(f"Downloaded {downloaded:,} bytes...")
                        
        print(f"\nDownload finished! Extracting {zip_path}...")
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.printdir()
            z.extractall(DEST_DIR)
        print("Extraction complete!")
    else:
        print("Failed to download with status code:", resp.status_code)
except Exception as e:
    print("Download exception:", e)
