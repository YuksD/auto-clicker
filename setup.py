from cx_Freeze import setup, Executable
import sys
import os

# Build klasörünü temizle
if os.path.exists("build"):
    try:
        import shutil
        shutil.rmtree("build")
    except:
        pass

# Build Options
build_exe_options = {
    "packages": [
        "os", 
        "sys",
        "json", 
        "time",
        "threading",
        "tkinter",
        "pyautogui", 
        "keyboard",
        "dataclasses",
        "typing"
    ],
    "includes": [
        "tkinter",
        "tkinter.ttk",
        "tkinter.messagebox",
        "tkinter.filedialog",
        "tkinter.simpledialog"
    ],
    "excludes": [
        "tkinter.test",  # Test modüllerini çıkar
        "unittest",      # Test modüllerini çıkar
        "test",         # Test modüllerini çıkar
        "distutils",    # Gereksiz modülleri çıkar
        "pip",          # Gereksiz modülleri çıkar
        "setuptools"    # Gereksiz modülleri çıkar
    ],
    "include_msvcr": True,
    "optimize": 2,
    "build_exe": "build/Otomasyon",  # Çıktı klasörü
    "zip_include_packages": "*",
    "zip_exclude_packages": []
}

# Executable
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Windows'ta GUI modu

executables = [
    Executable(
        script="automation.py",
        base=base,
        target_name="Otomasyon.exe",
        icon=None,  # İkon eklemek isterseniz: "path/to/icon.ico"
        shortcut_name="Otomasyon",
        shortcut_dir="DesktopFolder"
    )
]

setup(
    name="Otomasyon",
    version="1.0",
    description="Otomasyon Uygulaması",
    author="Your Name",  # İsteğe bağlı
    options={"build_exe": build_exe_options},
    executables=executables
)