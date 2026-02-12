import os
import glob
import shutil

INBOX_DIR = "/opt/airflow/inbox"
TARGET_DIR = "/opt/airflow/temp/data"

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)

    files = sorted(glob.glob(os.path.join(INBOX_DIR, "*.csv")), key=os.path.getmtime, reverse=True)
    if not files:
        raise FileNotFoundError(f"Aucun CSV trouvé dans {INBOX_DIR}")

    latest = files[0]
    dst = os.path.join(TARGET_DIR, os.path.basename(latest))
    shutil.copy2(latest, dst)
    print(f"[COPY] {latest} -> {dst}")

if __name__ == "__main__":
    main()
