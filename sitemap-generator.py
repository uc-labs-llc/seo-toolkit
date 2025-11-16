import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
import xml.etree.ElementTree as ET

# Configuration for the XML namespace
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
ACCEPTED_EXTENSIONS = ('.html', '.htm', '.php', '.asp', '.aspx', '.js', '.css', '.xml', '.json')

class LocalSitemapGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Penta5W Local File Sitemap XML Generator")
        master.geometry("750x600")

        # Configure style
        style = ttk.Style()
        style.configure('TFrame', background='#e6f0ff')
        style.configure('TLabel', background='#e6f0ff', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)

        # Main frame
        self.main_frame = ttk.Frame(master, padding="15 15 15 15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Input Variables
        self.root_folder_var = tk.StringVar(value="") 
        self.base_url_var = tk.StringVar(value="https://yourdomain.com") 
        self.default_priority_var = tk.StringVar(value="0.5")
        self.default_changefreq_var = tk.StringVar(value="monthly")
        self.status_var = tk.StringVar(value="Ready to index files...")

        self.setup_ui()
        
    def setup_ui(self):
        # 1. Folder & URL Input Frame
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill='x', pady=10)

        # Root Folder Selector
        ttk.Label(input_frame, text="1. Select Root Folder (e.g., your 'public_html' or 'dist' directory):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        
        self.folder_entry = ttk.Entry(input_frame, textvariable=self.root_folder_var, width=60)
        self.folder_entry.grid(row=1, column=0, sticky="ew", pady=5, padx=5)
        
        select_button = ttk.Button(input_frame, text="Browse...", command=self.select_folder)
        select_button.grid(row=1, column=1, sticky="e", pady=5, padx=5)
        
        input_frame.columnconfigure(0, weight=1) # Allow folder entry to expand

        # Base URL Input (UPDATED TEXT)
        ttk.Label(input_frame, text="2. Enter Base Public URL (Used to build the XML links, e.g., https://yourdomain.com):").grid(row=2, column=0, sticky="w", pady=5, padx=5, columnspan=2)
        self.url_entry = ttk.Entry(input_frame, textvariable=self.base_url_var, width=80)
        self.url_entry.grid(row=3, column=0, sticky="ew", pady=5, padx=5, columnspan=2)

        # Separator
        ttk.Separator(self.main_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 3. Sitemap Defaults Frame
        defaults_frame = ttk.Frame(self.main_frame)
        defaults_frame.pack(fill='x', pady=5)
        
        # Default Priority
        ttk.Label(defaults_frame, text="Default Priority (0.0 to 1.0):").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.priority_entry = ttk.Entry(defaults_frame, textvariable=self.default_priority_var, width=10)
        self.priority_entry.grid(row=0, column=1, sticky="w", pady=5, padx=5)

        # Default Change Frequency
        ttk.Label(defaults_frame, text="Default Change Frequency:").grid(row=0, column=2, sticky="w", pady=5, padx=5, columnspan=2)
        self.changefreq_options = ["always", "hourly", "daily", "weekly", "monthly", "yearly", "never"]
        self.changefreq_combo = ttk.Combobox(defaults_frame, textvariable=self.default_changefreq_var, values=self.changefreq_options, state="readonly", width=10)
        self.changefreq_combo.grid(row=0, column=4, sticky="w", pady=5, padx=5)
        
        # 4. Control Button
        self.generate_button = ttk.Button(self.main_frame, text="3. Generate Sitemap from Local Files", command=self.start_indexing)
        self.generate_button.pack(fill='x', pady=20)

        # 5. Status and Logging Area
        ttk.Label(self.main_frame, text="Current Status:", font=('Arial', 10, 'bold')).pack(fill='x', pady=(10, 5))
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=700, relief="sunken", padding="5", background='white')
        self.status_label.pack(fill='x', pady=5)
        
        ttk.Label(self.main_frame, text="File Indexing Log:", font=('Arial', 10, 'bold')).pack(fill='x', pady=(10, 5))
        self.log_text = tk.Text(self.main_frame, height=10, wrap=tk.WORD, state=tk.DISABLED, background='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def select_folder(self):
        """Opens a dialog to select the root folder."""
        folder_selected = filedialog.askdirectory(title="Select Root Folder of Website")
        if folder_selected:
            self.root_folder_var.set(folder_selected)
            self.set_status(f"Folder selected: {folder_selected}")

    def update_log(self, message):
        """Updates the text log and scrolls to the bottom."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def set_status(self, message):
        """Updates the status label."""
        self.status_var.set(message)
        self.master.update_idletasks() # Force UI update

    def start_indexing(self):
        """Validates inputs and starts the file indexing process."""
        root_folder = self.root_folder_var.get().strip()
        base_url = self.base_url_var.get().strip()

        if not root_folder or not os.path.isdir(root_folder):
            messagebox.showerror("Error", "Please select a valid root folder.")
            return

        if not base_url.startswith(('http://', 'https://')):
            messagebox.showerror("Error", "Base URL must start with 'http://' or 'https://'.")
            return
            
        if not base_url.endswith('/'):
            base_url += '/'

        # Clear logs
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        self.generate_button.config(state=tk.DISABLED)
        self.set_status("Indexing local files...")

        try:
            url_list = self.index_local_files(root_folder, base_url)
            if url_list:
                self.generate_and_save_xml(url_list)
            else:
                self.set_status("Indexing complete. No accepted files found in the directory.")

        except Exception as e:
            messagebox.showerror("Critical Error", f"A critical error occurred: {e}")
            self.set_status("Failed to generate sitemap due to a critical error.")
            
        finally:
            self.generate_button.config(state=tk.NORMAL)

    def index_local_files(self, root_folder, base_url):
        """Walks the directory tree, converts file paths to URLs, and returns a list of URLs."""
        url_list = []
        
        # List of directories to skip (common development folders)
        SKIP_DIRS = {'.git', 'node_modules', '__pycache__', 'venv', 'tmp', 'temp', 'logs'}

        for dirpath, dirnames, filenames in os.walk(root_folder):
            
            # Modify dirnames in place to skip unwanted directories on the next iteration
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                
                # Check for accepted extensions
                if filename.lower().endswith(ACCEPTED_EXTENSIONS):
                    
                    # 1. Get the path relative to the root folder
                    relative_path = os.path.relpath(file_path, root_folder)
                    
                    # 2. Convert OS path separators to URL forward slashes
                    url_path = relative_path.replace(os.path.sep, '/')
                    
                    # 3. Handle the index file at the root (e.g., index.html -> /)
                    if url_path.lower() in ['index.html', 'index.htm', 'index.php']:
                        if dirpath == root_folder:
                             url = base_url # e.g., https://yourdomain.com/
                        else:
                             # For index files in subdirectories, use the directory URL
                             url = base_url + os.path.relpath(dirpath, root_folder).replace(os.path.sep, '/') + '/'
                             
                    else:
                        # Standard file URL
                        url = base_url + url_path
                    
                    # 4. Get last modification date (timestamp to ISO format)
                    try:
                        timestamp = os.path.getmtime(file_path)
                        lastmod = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
                    except OSError:
                        lastmod = datetime.now().strftime("%Y-%m-%d")

                    url_list.append({'loc': url, 'lastmod': lastmod})
                    self.update_log(f"Indexed: {url}")

        return url_list

    def generate_and_save_xml(self, urls):
        """Generates the sitemap XML structure and prompts the user to save it."""
        try:
            # Get user-defined defaults
            default_priority = self.default_priority_var.get()
            default_changefreq = self.default_changefreq_var.get()

            # Register namespace
            ET.register_namespace('', SITEMAP_NS)
            urlset = ET.Element('urlset', xmlns=SITEMAP_NS)
            
            for item in urls:
                url_elem = ET.SubElement(urlset, 'url')
                
                loc = ET.SubElement(url_elem, 'loc')
                loc.text = item['loc']
                
                lastmod = ET.SubElement(url_elem, 'lastmod')
                lastmod.text = item['lastmod'] # Uses file's last modified time

                changefreq = ET.SubElement(url_elem, 'changefreq')
                changefreq.text = default_changefreq
                
                priority = ET.SubElement(url_elem, 'priority')
                priority.text = default_priority
                
            # Pretty print XML
            def prettify(elem):
                from xml.dom import minidom
                rough_string = ET.tostring(elem, 'utf-8')
                reparsed = minidom.parseString(rough_string)
                return reparsed.toprettyxml(indent="  ")

            xml_content = prettify(urlset)

            # Prompt the user to save the XML file
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xml",
                filetypes=[("XML Sitemap files", "*.xml")],
                title="Save Sitemap XML File"
            )

            if filepath:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(xml_content) 
                self.set_status(f"SUCCESS! Sitemap saved to: {os.path.basename(filepath)} with {len(urls)} URLs.")
                messagebox.showinfo("Success", f"Sitemap.xml generated and saved successfully with {len(urls)} URLs!")
            else:
                self.set_status("XML generation complete, but file save was cancelled.")
                
        except Exception as e:
            self.set_status(f"Error during XML generation: {e}")
            messagebox.showerror("XML Error", f"Failed to generate or save XML: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = LocalSitemapGeneratorApp(root)
    root.mainloop()
