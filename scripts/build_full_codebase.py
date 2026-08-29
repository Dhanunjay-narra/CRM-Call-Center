import os
import sys

BASE_DIR = r"c:\Users\DHANUNJAY\OneDrive\Desktop\git project folders\git8"

def write_code(rel_path, code):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code.strip() + "\n")
    print(f"Created: {rel_path} ({len(code.splitlines())} lines)")

def main():
    print("Beginning comprehensive enterprise domain expansion for CallSphere CRM...")

if __name__ == "__main__":
    main()
