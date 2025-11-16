import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Toplevel, scrolledtext
import os
import json
from datetime import datetime

class SeoHtmlGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Penta5W SEO HTML Boilerplate Generator (A+ Edition)")
        master.geometry("800x900") # Increased size for new features

        # Set a professional style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f4f8')
        style.configure('TLabel', background='#f0f4f8', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=6)
        style.configure('TEntry', padding=4)
        style.configure('SchemaType.TLabel', font=('Arial', 10, 'bold'), foreground='#0056b3')
        style.configure('Output.TFrame', background='#e0e8f0', borderwidth=2, relief='groove')
        style.configure('Output.TLabel', background='#e0e8f0', font=('Arial', 11, 'bold'))

        # Main frame with padding
        self.main_frame = ttk.Frame(master, padding="15 15 15 15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Variables ---
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
            # JSON-LD variables
            "schema_type": tk.StringVar(value="TechArticle"), 
            "json_ld_name": tk.StringVar(value="Example Organization"),
            "json_ld_logo": tk.StringVar(value="https://www.example.com/images/logo-placeholder.png"),
            # New Output Format variable
            "output_format": tk.StringVar(value="full_html") 
        }
        
        # State variable to hold Q&A pairs for FAQPage
        self.faq_pairs = []

        # --- UI Setup ---
        self.setup_header()
        last_row = self.setup_input_fields(row_start=1)
        last_row = self.setup_output_format(row_start=last_row) # New Output Format Section
        
        # Generate Button 
        generate_button = ttk.Button(self.main_frame, text="Generate & Save File", command=self.generate_html)
        generate_button.grid(row=last_row, column=0, columnspan=2, pady=(20, 0), sticky="ew")

    def setup_header(self):
        # Header Section with Title and Import/Export Buttons
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

    def clear_on_focus(self, event):
        """Clears the entry field if its current content is the initial default value."""
        entry = event.widget
        current_text = entry.get()
        default_text = getattr(entry, 'default_value', '')

        if current_text == default_text:
            entry.delete(0, tk.END)
            entry.unbind('<FocusIn>')

    def create_input_row(self, label_text, var_key, row):
        """Helper to create a label and entry field."""
        label = ttk.Label(self.main_frame, text=label_text + ":")
        label.grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(self.main_frame, textvariable=self.vars[var_key], width=80)
        entry.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        entry.default_value = self.vars[var_key].get()
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

        # Separator for JSON-LD Setup
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10)
        current_row += 1
        
        # --- JSON-LD SCHEMA SELECTION AND INPUT ---
        
        # Schema Type Dropdown
        schema_frame = ttk.Frame(self.main_frame)
        schema_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=5)
        ttk.Label(schema_frame, text="JSON-LD Schema Type:", style='SchemaType.TLabel').pack(side=tk.LEFT, padx=(0, 10))

        schema_options = ["TechArticle", "FAQPage"]
        self.schema_combo = ttk.Combobox(schema_frame, textvariable=self.vars["schema_type"], values=schema_options, state="readonly", width=20)
        self.schema_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.schema_combo.bind("<<ComboboxSelected>>", self.toggle_schema_inputs)

        current_row += 1

        # JSON-LD Publisher/Organization Inputs (Visible for all schemas)
        self.publisher_inputs_frame = ttk.Frame(self.main_frame)
        self.publisher_inputs_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew")
        current_row += 1
        
        r = 0
        self.create_input_row_in_frame(self.publisher_inputs_frame, "JSON-LD Publisher Name (Organization)", "json_ld_name", r)
        r += 1
        self.create_input_row_in_frame(self.publisher_inputs_frame, "JSON-LD Logo URL", "json_ld_logo", r)
        
        # FAQPage Specific Inputs (Hidden by default)
        self.faq_inputs_frame = ttk.Frame(self.main_frame)
        self.faq_inputs_frame.grid(row=current_row, column=0, columnspan=2, sticky="ew")
        current_row += 1
        
        ttk.Label(self.faq_inputs_frame, text=f"Currently {len(self.faq_pairs)} Q&A pairs added.", name="faq_count_label").grid(row=0, column=0, sticky="w", pady=5)
        
        manage_faq_button = ttk.Button(self.faq_inputs_frame, text="Manage Q&A Pairs for FAQPage", command=self.open_faq_manager)
        manage_faq_button.grid(row=0, column=1, sticky="e", pady=5, padx=(10, 0))
        
        self.faq_inputs_frame.grid_remove() # Hide this frame initially
        
        # Final Separator before Output Format
        ttk.Separator(self.main_frame, orient='horizontal').grid(row=current_row, column=0, columnspan=2, sticky="ew", pady=10)
        current_row += 1

        # Configure columns to expand
        self.main_frame.columnconfigure(1, weight=1)
        self.publisher_inputs_frame.columnconfigure(1, weight=1)
        self.faq_inputs_frame.columnconfigure(0, weight=1) 
        
        return current_row

    def create_input_row_in_frame(self, frame, label_text, var_key, row):
        """Helper to create a label and entry field within a specific frame."""
        label = ttk.Label(frame, text=label_text + ":")
        label.grid(row=row, column=0, sticky="w", pady=2)
        entry = ttk.Entry(frame, textvariable=self.vars[var_key], width=80)
        entry.grid(row=row, column=1, sticky="ew", pady=2, padx=(10, 0))
        
        entry.default_value = self.vars[var_key].get()
        entry.bind('<FocusIn>', self.clear_on_focus)

    def setup_output_format(self, row_start):
        """Sets up the radio buttons for selecting the output file format."""
        
        output_frame = ttk.Frame(self.main_frame, style='Output.TFrame', padding="10")
        output_frame.grid(row=row_start, column=0, columnspan=2, sticky="ew", pady=10)
        
        ttk.Label(output_frame, text="Select Output Format:", style='Output.TLabel').pack(anchor='w', pady=(0, 5))
        
        # Full HTML option
        ttk.Radiobutton(output_frame, 
                        text="1. Full HTML Page (.html): Includes <html> and <body> boilerplate.", 
                        variable=self.vars["output_format"], 
                        value="full_html").pack(anchor='w', padx=10)
                        
        # Header Content only option
        ttk.Radiobutton(output_frame, 
                        text="2. Header Content Only (.txt): Optimized tags for pasting inside your existing <head>.", 
                        variable=self.vars["output_format"], 
                        value="header_only").pack(anchor='w', padx=10)
        
        return row_start + 1 # Return the next available row

        
    def toggle_schema_inputs(self, event=None):
        """Shows/hides inputs based on the selected schema type."""
        selected_schema = self.vars["schema_type"].get()
        
        self.publisher_inputs_frame.grid()
        
        if selected_schema == "FAQPage":
            self.faq_inputs_frame.grid()
        else:
            self.faq_inputs_frame.grid_remove()
            
    def update_faq_count_label(self):
        """Updates the label showing the number of Q&A pairs."""
        try:
            # Access the dynamically named label widget
            count_label = self.faq_inputs_frame.nametowidget(f".{self.faq_inputs_frame._w}.faq_count_label")
            count_label.config(text=f"Currently {len(self.faq_pairs)} Q&A pairs added.")
        except:
             # This can fail if the app is closed during a pop-up interaction, handle gracefully.
             pass


    def open_faq_manager(self):
        """Opens a Toplevel window to manage Question and Answer pairs."""
        manager = Toplevel(self.master)
        manager.title("FAQPage Q&A Manager")
        manager.geometry("600x450")
        manager.transient(self.master) 
        manager.grab_set() 

        frame = ttk.Frame(manager, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # --- Question Input ---
        ttk.Label(frame, text="Question:").pack(fill='x', pady=(0, 2))
        question_entry = ttk.Entry(frame, width=70)
        question_entry.pack(fill='x', pady=(0, 10))

        # --- Answer Input ---
        ttk.Label(frame, text="Answer:").pack(fill='x', pady=(0, 2))
        answer_text = scrolledtext.ScrolledText(frame, height=5, wrap=tk.WORD)
        answer_text.pack(fill='x', pady=(0, 10))

        def add_pair():
            q = question_entry.get().strip()
            a = answer_text.get("1.0", tk.END).strip()
            
            if q and a:
                self.faq_pairs.append({"question": q, "answer": a})
                list_pairs() 
                question_entry.delete(0, tk.END) 
                answer_text.delete("1.0", tk.END)
                self.update_faq_count_label()
            else:
                messagebox.showerror("Error", "Both Question and Answer fields must be filled.")

        ttk.Button(frame, text="Add Q&A Pair", command=add_pair).pack(fill='x', pady=(5, 10))

        # --- List Display ---
        ttk.Label(frame, text="Current Q&A Pairs:").pack(fill='x', pady=(5, 2))
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        listbox = tk.Listbox(list_frame, height=8, selectmode=tk.SINGLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        list_scrollbar = ttk.Scrollbar(list_frame, command=listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=list_scrollbar.set)

        def list_pairs():
            listbox.delete(0, tk.END)
            for i, pair in enumerate(self.faq_pairs):
                listbox.insert(tk.END, f"{i+1}. Q: {pair['question']}")

        def remove_pair():
            selected_indices = listbox.curselection()
            if selected_indices:
                index_to_remove = selected_indices[0]
                self.faq_pairs.pop(index_to_remove)
                list_pairs()
                self.update_faq_count_label()
            else:
                messagebox.showwarning("Warning", "Select a pair to remove first.")

        ttk.Button(frame, text="Remove Selected Pair", command=remove_pair).pack(fill='x', pady=(10, 5))
        
        list_pairs() 
        manager.wait_window()
        
    def get_current_settings(self):
        """Returns a dictionary of all current settings from the form, including the FAQ pairs."""
        settings = {key: var.get().strip() for key, var in self.vars.items()}
        settings['faq_pairs'] = self.faq_pairs
        return settings

    def import_settings(self):
        """Reads a JSON file, and updates form variables and FAQ pairs."""
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

            for key, value in settings.items():
                if key in self.vars:
                    self.vars[key].set(str(value))
            
            if 'faq_pairs' in settings and isinstance(settings['faq_pairs'], list):
                self.faq_pairs = settings['faq_pairs']
                self.update_faq_count_label()
                self.toggle_schema_inputs() 

            messagebox.showinfo("Import Success", f"Successfully loaded settings from:\n{os.path.basename(filepath)}")

        except Exception as e:
            messagebox.showerror("Import Error", f"An unexpected error occurred during import: {e}")

    def export_settings(self):
        """Opens a file dialog and saves current form variables and FAQ pairs to a JSON file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Settings Files", "*.json")],
            title="Save Current Settings to JSON File"
        )
        if not filepath:
            return

        try:
            settings_data = self.get_current_settings()
            if not settings_data['faq_pairs']:
                del settings_data['faq_pairs']
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=4)
            
            messagebox.showinfo("Export Success", f"Successfully saved settings to:\n{os.path.basename(filepath)}")

        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during export: {e}")


    def generate_json_ld(self, v):
        """Generates the structured data script based on the selected schema type."""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        schema_type = v['schema_type']
        
        data = {"@context": "https://schema.org"}
        
        if schema_type == "TechArticle":
            data.update({
                "@type": "TechArticle",
                "headline": v['title'], 
                "alternativeHeadline": "A generic headline for the demo tech article.", 
                "articleBody": v['description'], 
                "articleSection": ["Introduction", "Key Concepts", "Conclusion"],
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
                    "email": "info@example.com", 
                    "logo": {
                        "@type": "ImageObject",
                        "url": v['json_ld_logo']
                    }
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": v['site_url']
                }
            })
            
        elif schema_type == "FAQPage":
            if not v['faq_pairs']:
                return "<!-- WARNING: FAQPage schema selected, but no Q&A pairs were added. The generated schema will be empty. -->"
            
            faq_list = []
            for pair in v['faq_pairs']:
                faq_list.append({
                    "@type": "Question",
                    "name": pair['question'],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": pair['answer']
                    }
                })

            data.update({
                "@type": "FAQPage",
                "headline": v['title'],
                "url": v['site_url'],
                "mainEntity": faq_list
            })
            
        else:
            return "<!-- ERROR: JSON-LD Schema Type not recognized or missing. -->"

        json_content = json.dumps(data, indent=4)
        
        return f"""<script type="application/ld+json">
{json_content}
</script>"""
        
    def generate_header_content(self, v):
        """Generates the content to be placed directly inside an existing <head> tag."""
        
        json_ld_block = self.generate_json_ld(v)

        header_content = f"""
    <!-- Google Tag (gtag.js) -->
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
"""
        return header_content.strip()

    def generate_full_html_content(self, v):
        """Constructs the full HTML document string."""
        
        header_content = self.generate_header_content(v)

        # Construct the HTML structure
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

{header_content}

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
        """Saves the content based on the selected output format."""
        
        v = self.get_current_settings()
        output_format = v['output_format']
        
        try:
            # Check for FAQPage validation
            if v["schema_type"] == "FAQPage" and not self.faq_pairs:
                messagebox.showwarning("Missing Data", "You selected 'FAQPage' but didn't add any Q&A pairs. The generated schema will be empty.")

            if output_format == "full_html":
                # Save as a full HTML file
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".html",
                    filetypes=[("HTML files", "*.html")],
                    title="Choose Location and File Name for Full HTML"
                )
                if not filepath: return
                output_content = self.generate_full_html_content(v)
            
            elif output_format == "header_only":
                # Save as a text file containing only header content
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text files", "*.txt")],
                    title="Choose Location and File Name for Header Content (Pasteable)"
                )
                if not filepath: return
                output_content = self.generate_header_content(v)
            
            else:
                messagebox.showerror("Error", "Invalid output format selected.")
                return

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(output_content)

            messagebox.showinfo(
                "Success",
                f"Successfully generated and saved {output_format.replace('_', ' ').title()} file:\n{os.path.basename(filepath)}"
            )
            
            # --- Logic to clear fields after success ---
            fields_to_clear = ['title', 'description', 'keywords', 'author']
            for key in fields_to_clear:
                self.vars[key].set("")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = SeoHtmlGeneratorApp(root)
    root.mainloop()
