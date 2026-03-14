"""
Create a zip archive of the project, excluding unnecessary directories.
"""

import os
import zipfile
import shutil
from pathlib import Path


def create_project_zip():
    """Create a zip archive excluding venv, .vscode, __pycache__"""

    project_dir = Path.cwd()
    zip_filename = "Beaver_Choice_Paper_Project.zip"

    # Directories and files to exclude
    exclude_dirs = {"venv", ".vscode", "__pycache__", ".git"}
    exclude_extensions = {".pyc", ".pyo", ".pyd"}
    exclude_files = {
        "Beaver_Choice_Paper.zip",
        "Beaver_Choice_Paper_Project.zip",
        "create_zip.py",
    }

    # Create zip file
    with zipfile.ZipFile(zip_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            # Remove excluded directories from traversal
            dirs[:] = [
                d for d in dirs if d not in exclude_dirs and not d.startswith(".")
            ]

            for file in files:
                # Skip excluded files
                if file in exclude_files or file.endswith(tuple(exclude_extensions)):
                    continue

                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, project_dir)

                try:
                    zipf.write(file_path, arcname)
                    print(f"  ✓ Added: {arcname}")
                except Exception as e:
                    print(f"  ⚠️  Skipped {arcname}: {e}")

    # Get zip file info
    zip_path = Path(zip_filename)
    if zip_path.exists() and zip_path.stat().st_size > 100:
        size_bytes = zip_path.stat().st_size
        size_mb = round(size_bytes / (1024 * 1024), 2)

        print("\n" + "=" * 70)
        print("✅ ZIP ARCHIVE CREATED SUCCESSFULLY")
        print("=" * 70)
        print(f"\nFilename: {zip_filename}")
        print(f"Size: {size_bytes:,} bytes ({size_mb} MB)")
        print(f"Location: {os.path.abspath(zip_filename)}")

        print("\n📦 EXCLUDED DIRECTORIES:")
        print("  • venv (virtual environment)")
        print("  • .vscode (IDE configuration)")
        print("  • __pycache__ (Python cache)")
        print("  • .git (version control)")

        print("\n✨ INCLUDED IN ARCHIVE:")
        print("  • All Python source files (*.py)")
        print("  • All CSV data files (*.csv)")
        print("  • Workflow diagram (*.png)")
        print("  • Documentation (*.md)")
        print("  • Configuration files (requirements.txt, .env)")

        return True
    else:
        print("❌ Error: Zip file was not created or is empty")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Creating Project Archive...")
    print("=" * 70 + "\n")

    create_project_zip()
