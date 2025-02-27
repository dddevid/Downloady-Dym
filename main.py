import os
import sys
import asyncio
import httpx
import aiofiles
import customtkinter as ctk
import threading
import time
import importlib.util
import winreg
from urllib.parse import urlparse
from tkinter import filedialog

DEFAULT_THREADS = 4

# Verifica se il percorso è già stato aggiunto
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PATH_MARKER = os.path.join(SCRIPT_DIR, ".path_added")

def add_to_path():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment", 0, winreg.KEY_ALL_ACCESS) as key:
            current_path, _ = winreg.QueryValueEx(key, "Path")
            if SCRIPT_DIR not in current_path:
                new_path = f"{current_path};{SCRIPT_DIR}"
                winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
                with open(PATH_MARKER, "w") as f:
                    f.write("Path added")
                print(f"Added {SCRIPT_DIR} to PATH. Restart terminal to apply changes.")
    except Exception as e:
        print(f"Failed to update PATH: {e}")

if not os.path.exists(PATH_MARKER):
    add_to_path()

# Crea un alias eseguibile se necessario
if sys.platform.startswith("win"):
    script_name = "Downloady.bat"
    script_path = os.path.join(SCRIPT_DIR, script_name)
    if not os.path.exists(script_path):
        with open(script_path, "w") as f:
            f.write(f"@echo off\npy \"{__file__}\" %*")

print(f"Run 'Downloady' to start the application.")

class DownloadManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Download Manager")
        self.geometry("500x350")
        ctk.set_appearance_mode("dark")
        
        self.url_entry = ctk.CTkEntry(self, placeholder_text="Enter file URL", width=400)
        self.url_entry.pack(pady=10)
        
        self.download_button = ctk.CTkButton(self, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self, text="Waiting for download...")
        self.status_label.pack(pady=10)
        
        self.extension_label = ctk.CTkLabel(self, text="No extension loaded")
        self.extension_label.pack(pady=10)
        
        self.num_threads = DEFAULT_THREADS
        self.extension = None

    def start_download(self):
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="Please enter a valid URL")
            return
        
        filename = os.path.basename(urlparse(url).path) or "downloaded_file"
        save_path = filedialog.asksaveasfilename(defaultextension="", initialfile=filename, title="Save File As")
        if not save_path:
            self.status_label.configure(text="Download cancelled")
            return
        
        self.status_label.configure(text="Downloading...")
        self.progress_bar.set(0)
        
        thread = threading.Thread(target=self.run_download, args=(url, save_path), daemon=True)
        thread.start()
    
    def run_download(self, url, save_path):
        if self.extension and hasattr(self.extension, "process_download"):
            self.status_label.configure(text="Download Started with Extension!")
            try:
                self.extension.process_download(url, save_path, self.progress_bar.set)
            except Exception as e:
                self.status_label.configure(text=f"Extension Error: {e}")
            return
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self.download_file(url, save_path))
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
    
    async def download_file(self, url, dest):
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                
                if total_size == 0:
                    self.status_label.configure(text="Invalid URL or unknown file size")
                    return
                
                start_time = time.time()
                
                async with aiofiles.open(dest, 'wb') as f:
                    async for chunk in response.aiter_bytes(1024 * 128):
                        await f.write(chunk)
                        elapsed_time = time.time() - start_time
                        speed = (total_size / elapsed_time) / (1024 * 1024) if elapsed_time > 0 else 0
                        self.status_label.configure(text=f"Downloading... Speed: {speed:.2f} MBps")
                        await asyncio.sleep(0.1)  # Allow GUI updates
                
                self.status_label.configure(text="Download Complete!")
                self.progress_bar.set(1)
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}")
    
    def load_extension(self, extension_path):
        if not os.path.exists(extension_path) or not extension_path.endswith(".py"):
            print("Invalid extension file.")
            return
        
        try:
            print(f"Trying to load extension from: {extension_path}")
            spec = importlib.util.spec_from_file_location("extension", extension_path)
            if spec is None or spec.loader is None:
                raise ImportError("Failed to load extension spec.")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self.extension = module
            
            if hasattr(module, "Name") and hasattr(module, "Devs"):
                self.extension_label.configure(text=f"! Extension {module.Name[0]} made by {', '.join(module.Devs)} Loaded !")
                print(f"Extension {module.Name[0]} by {', '.join(module.Devs)} successfully loaded.")
            else:
                self.extension_label.configure(text="Loaded extension missing metadata!")
                print("Warning: Loaded extension is missing metadata.")
        except Exception as e:
            print(f"Failed to load extension: {e}")
            self.status_label.configure(text=f"Extension Load Error: {e}")

if __name__ == "__main__":
    app = DownloadManager()
    if "-e" in sys.argv:
        try:
            index = sys.argv.index("-e")
            extension_path = sys.argv[index + 1]
            app.load_extension(extension_path)
        except (IndexError, ValueError):
            print("Invalid extension file, skipping.")
    app.mainloop()
