import os
import sys

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"

def write_f(rel_path, content):
    p = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: {rel_path} ({len(content.splitlines())} lines)")

def main():
    print("Generating comprehensive Frontend UI component library and hooks...")

if __name__ == "__main__":
    main()
