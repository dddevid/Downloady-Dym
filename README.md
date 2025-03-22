# Downloady - Download Manager

Downloady is a Python application that allows you to download files from the Internet with a graphical interface, supports customizable extensions, and automatically adds itself to the Windows `PATH` for quick access.

## Main Features
- **Graphical Interface:** Simple and intuitive with `customtkinter`.
- **Multi-threaded Download Support:** Fast and reliable downloads.
- **Customizable Extensions:** Load custom plugins to add new functionalities.
- **Automatic PATH Addition:** Accessible from the terminal with the `Downloady` command.

---

## Installation and First Run

### 1. Install Python
Make sure you have **Python 3.10 or later** installed. You can download it from:
[https://www.python.org/downloads/](https://www.python.org/downloads/)

### 2. Install Dependencies
Open a terminal (PowerShell or CMD) and navigate to the folder containing `Downloady`. Then run:
```sh
pip install -r requirements.txt
```

### 3. First Run
Run the script once to add it to the `PATH`:
```sh
python main.py
```
After the first run, close and reopen the terminal. Now you can launch the application with:
```sh
Downloady
```

---

## How to Use Downloady

1. **Enter the file URL** in the text field.
2. **Click "Download"** and choose where to save the file.
3. **Wait for the download to complete.**

---

## Using Extensions
Extensions are Python scripts that extend Downloady's functionalities.

### Installing an Extension
To use an extension, pass its path to the `Downloady` command:
```sh
Downloady -e extensions\ytube.py
```
**Note:** If the path contains spaces, enclose it in quotes.

### Creating Your Own Extension
An extension is a simple Python script that must implement the function:
```python
def process_download(url, save_path, progress_callback):
    # Code to handle the custom download
```
And must contain these variables:
```python
Name = ["Extension Name"]
Devs = ["Your Name"]
```
Save the file with a `.py` extension and load it with the `Downloady -e` command.

---

## Troubleshooting
- **Downloady is not recognized in the terminal**
  - Ensure you have run `python main.py` at least once.
  - Restart the terminal to apply `PATH` changes.
  - Check with `echo %PATH%` if the Downloady folder is present.

- **The extension does not load**
  - Make sure the file is a valid `.py` script.
  - Ensure the file contains the `process_download` function.
  - Run with `Downloady -e "path\to\extension.py"`.

---

## License
This project is distributed under the MIT license. You can freely modify and redistribute it.

---

Happy Downloading! 🚀

