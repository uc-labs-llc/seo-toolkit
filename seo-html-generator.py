import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from datetime import datetime

class SeoHtmlGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title(" Penta5W.com SEO HTML Boilerplate Generator (A+ Edition)")
        master.geometry("800x750") # Slightly larger window

        # Set a professional style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f4f8')
        style.configure('TLabel', background='#f0f4f8', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        style.configure('TEntry', padding=4)

        # Main frame with padding
        self.main_frame = ttk.Frame(master, padding="15 15 15 15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Header Section with Title and Import/Export Buttons ---
        header_frame = ttk.Frame(self.main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="ew")
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(header_frame, text="Generate Advanced SEO HTML Boilerplate", font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, sticky="w")

        # Buttons on the right side of the header
        button_frame = ttk.Frame(header_frame)
        button_frame.grid(row=0, column=1, sticky="e")

        import_button = ttk.Button(button_frame, text="Import Settings", command=self.import_settings)
        import_button.pack(side=tk.LEFT, padx=(5, 5))
        
        export_button = ttk.Button(button_frame, text="Save Current Settings to File", command=self.export_settings)
        export_button.pack(side=tk.LEFT, padx=(5, 0))
        # -----------------------------------------------------------

        # Create a dictionary to hold all input variables (Now using generic DEMO data)
        self.vars = {
            "title": tk.StringVar(value="Example Page Title"),
            "description": tk.StringVar(value="This is a generic, SEO-optimized page description for a demo project."),
            "keywords": tk.StringVar(value="demo, template, boilerplate, html, seo"),
            "author": tk.StringVar(value="Demo Author"),
            "site_url": tk.StringVar(value="https://www.example.com/demo-page.html"),
            "image_url": tk.StringVar(value="https://www.example.com/images/social-image-placeholder.png"),
            "og_type": tk.StringVar(value="article"),
            "twitter_handle": tk.StringVar(value="@DemoHandle"),
            "gtag_id": tk.StringVar(value="G-XXXXXXXXXX"), 
            "json_ld_type": tk.StringVar(value="TechArticle"), 
            "json_ld_name": tk.StringVar(value="Example Organization"),
            "json_ld_logo": tk.StringVar(value="https://www.example.com/images/logo-placeholder.png")
        }

        # Setup Input Grid
        last_row = self.setup_input_fields(row_start=1)
        
        # Generate Button (Correctly positioned at the very bottom)
        generate_button = ttk.Button(self.main_frame, text="Generate & Save HTML File", command=self.generate_html)
        generate_button.grid(row=last_row, column=0, columnspan=2, pady=(20, 0), sticky="ew")

    def clear_on_focus(self, event):
        """Clears the entry field if its current content is the initial default value."""
        entry = event.widget
        current_text = entry.get()
        default_text = getattr(entry, 'default_value', '')

        # Check if the current text matches the original default text
        if current_text == default_text:
            # Clear the entry
            entry.delete(0, tk.END)
            # Unbind the event so it doesn't clear again after the user has input content
            entry.unbind('<FocusIn>')

    def create_input_row(self, label_text, var_key, row):
        """Helper to create a label and entry field, binding the clear_on_focus event."""
        label = ttk.Label(self.main_frame, text=label_text + ":")
        label.grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(self.main_frame, textvariable=self.vars[var_key], width=80)
        entry.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        # Store the default value on the entry widget instance
        entry.default_value = self.vars[var_key].get()
        
        # Bind the focus event to clear the default text
        entry.bind('<FocusIn>', self.clear_on_focus)
        
        return row + 1

    def setup_input_fields(self, row_start):
        """Sets up all the necessary input fields."""
        current_row = row_start

        # Basic SEO Tags
        current_row = self.create_input_row("Page Title (Max 60 chars) [Headline]", "title", current_row)
        current_row = self.create_input_row("Meta Description [Article Body]", "description", current_row)
        current_row = self.create_input_row("Keywords (Comma Separated) [Schema Keywords]", "keywords", current_row)
        current_row = self.create_input_row("Author Name [Schema Author]", "author", current_row)

        # Separator for Gtag
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10)
        current_row += 1

        # Google Tag
        current_row = self.create_input_row("Google Analytics ID (G-XXXXX)", "gtag_id", current_row)

        # Separator for OpenGraph/Social
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10)
        current_row += 1

        # OpenGraph & Twitter Tags
        current_row = self.create_input_row("Canonical Page URL [Schema URL]", "site_url", current_row)
        current_row = self.create_input_row("Social Share Image URL [Schema Image]", "image_url", current_row)
        current_row = self.create_input_row("OpenGraph Type (e.g., article)", "og_type", current_row)
        current_row = self.create_input_row("Twitter Handle (@username)", "twitter_handle", current_row)

        # Separator for JSON-LD (Publisher/Organization details)
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10)
        current_row += 1

        # JSON-LD Inputs (For Publisher/Organization details in the TechArticle schema)
        current_row = self.create_input_row("JSON-LD Schema Type (Locked to TechArticle)", "json_ld_type", current_row)
        current_row = self.create_input_row("JSON-LD Publisher Name (e.g., Example Organization)", "json_ld_name", current_row)
        current_row = self.create_input_row("JSON-LD Logo URL", "json_ld_logo", current_row)
        
        # Configure columns to expand
        self.main_frame.columnconfigure(1, weight=1)

        return current_row

    def get_current_settings(self):
        """Returns a dictionary of all current settings from the form."""
        return {key: var.get().strip() for key, var in self.vars.items()}

    def import_settings(self):
        """Opens a file dialog, reads a JSON file, and updates form variables."""
        filepath = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON Settings Files", "*.json")],
            title="Select Settings JSON File to Import"
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Update the Tkinter variables
            for key, value in settings.items():
                if key in self.vars:
                    # Ensure value is a string before setting
                    self.vars[key].set(str(value))
            
            messagebox.showinfo("Import Success", f"Successfully loaded settings from:\n{os.path.basename(filepath)}")

        except FileNotFoundError:
            messagebox.showerror("Import Error", "File not found.")
        except json.JSONDecodeError:
            messagebox.showerror("Import Error", "Invalid JSON file format.")
        except Exception as e:
            messagebox.showerror("Import Error", f"An unexpected error occurred during import: {e}")

    def export_settings(self):
        """Opens a file dialog and saves current form variables to a JSON file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Settings Files", "*.json")],
            title="Save Current Settings to JSON File"
        )
        if not filepath:
            return

        try:
            settings_data = self.get_current_settings()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            
            messagebox.showinfo("Export Success", f"Successfully saved settings to:\n{os.path.basename(filepath)}")

        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during export: {e}")


    def generate_json_ld(self):
        """Generates the detailed TechArticle JSON-LD structured data script."""
        
        v = self.get_current_settings()
        current_date = datetime.now().strftime("%Y-%m-%d")

        # The JSON-LD structure based on your specific TechArticle template, now with DEMO content
        data = {
            "@context": "https://schema.org",
            "@type": "TechArticle",
            "headline": v['title'], 
            "alternativeHeadline": "A generic headline for the demo tech article.", # CHANGED to DEMO
            "articleBody": v['description'], 
            "articleSection": [
                "Demo Section 1: Introduction", # CHANGED to DEMO
                "Demo Section 2: Key Concepts", # CHANGED to DEMO
                "Demo Section 3: Conclusion",  # CHANGED to DEMO
            ],
            "keywords": v['keywords'], 
            "datePublished": current_date, 
            "dateModified": current_date, 
            "url": v['site_url'],
            "image": v['json_ld_logo'],
            "author": {
                "@type": "Person",
                "name": v['author']
            },
            "publisher": {
                "@type": "Organization",
                "name": v['json_ld_name'],
                "email": "info@example.com", # CHANGED to DEMO
                "logo": {
                    "@type": "ImageObject",
                    "url": v['json_ld_logo']
                }
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": v['site_url']
            }
        }

        # Use an indented dump for readability in the HTML output
        json_content = json.dumps(data, indent=4)
        
        return f"""<script type="application/ld+json">
{json_content}
</script>"""

    def generate_html_content(self):
        """Constructs the full HTML document string with updated tag order."""
        
        # Get all variables
        v = self.get_current_settings()

        # Generate JSON-LD block
        json_ld_block = self.generate_json_ld()

        # Construct the HTML structure
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <!-- Google Tag (gtag.js) - Uses G-XXXXXXXXXX by default -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={v['gtag_id']}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{v['gtag_id']}');
    </script>

    <!-- JSON-LD Structured Data (For Rich Snippets) -->
{json_ld_block}
    
    <!-- Canonical Link - High Priority -->
    <link rel="canonical" href="{v['site_url']}" />

    <title>{v['title']}</title>

    <!-- Basic Meta Tags for SEO -->
    <meta name="description" content="{v['description']}">
    <meta name="keywords" content="{v['keywords']}">
    <meta name="author" content="{v['author']}">

    <!-- External CSS for Consistency (Normalize.css) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.min.css">

    <!-- Comprehensive Favicon and Manifest Links - Uses root-relative URLs (/favicon.ico) -->
    <link rel="icon" href="/favicon.ico" sizes="any">
    <link rel="icon" href="/favicon-32x32.png" type="image/png" sizes="32x32">
    <link rel="icon" href="/favicon-16x16.png" type="image/png" sizes="16x16">
    <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">
    
    <!-- Open Graph / Facebook / LinkedIn Meta Tags -->
    <meta property="og:title" content="{v['title']}">
    <meta property="og:description" content="{v['description']}">
    <meta property="og:url" content="{v['site_url']}">
    <meta property="og:type" content="{v['og_type']}">
    <meta property="og:image" content="{v['image_url']}">

    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="{v['twitter_handle']}">
    <meta name="twitter:creator" content="{v['twitter_handle']}">
    <meta name="twitter:title" content="{v['title']}">
    <meta name="twitter:description" content="{v['description']}">
    <meta name="twitter:image" content="{v['image_url']}">
    
    <!-- Optional: Basic Styling for the Blank Page -->
    <style>
        body {{ font-family: sans-serif; margin: 20px; background-color: #f4f4f9; }}
        h1 {{ color: #333; }}
        code {{ background-color: #eee; padding: 2px 4px; border-radius: 3px; }}
        .header-info {{ border: 1px solid #ccc; padding: 15px; background-color: #fff; margin-bottom: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <div class="header-info">
        <h1>{v['title']}</h1>
        <p><strong>Description:</strong> {v['description']}</p>
        <p>This is your generated SEO-optimized HTML boilerplate page. All necessary meta tags, JSON-LD, and Google Analytics code are included in the <code>&lt;head&gt;</code> section.</p>
        <p>Start adding your main content here!</p>
    </div>

    <!-- START MAIN PAGE CONTENT HERE -->


    <!-- END MAIN PAGE CONTENT HERE -->
</body>
</html>
"""
        return html_content

    def generate_html(self):
        """Prompts the user to save the file (location and name) and writes the content."""
        try:
            # Open a file dialog to choose where to save the .html file
            filepath = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML files", "*.html")],
                title="Choose Location and File Name for HTML"
            )

            if not filepath:
                # User cancelled the dialog
                return

            html_output = self.generate_html_content()

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_output)

            messagebox.showinfo(
                "Success",
                f"Successfully generated and saved HTML file:\n{os.path.basename(filepath)}"
            )
            
            # --- Logic to clear fields after success ---
            # We clear these fields so the user is forced to enter new, specific data for the next page.
            fields_to_clear = ['title', 'description', 'keywords', 'author']
            for key in fields_to_clear:
                self.vars[key].set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == '__main__':
    # Initialize the main Tkinter window
    root = tk.Tk()
    # Create the application instance
    app = SeoHtmlGeneratorApp(root)
    # Start the Tkinter event loop
    root.mainloop()
