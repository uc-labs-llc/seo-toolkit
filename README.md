
The Complete SEO Toolkit

📈 Take Control of Your SEO and Get an A+ Rating

Welcome to the seo-toolkit! This open-source project provides two essential Python tools to help you take full control of your website's Search Engine Optimization (SEO) without spending thousands of dollars on expensive online services.

By combining the structural integrity provided by the HTML Generator and the critical feedback from the SEO Checker, and pairing this with the free, powerful data from Google Analytics and Google Search Console, you have a complete, self-managed toolkit to ensure your website is perfectly optimized. You will be able to achieve an A= rating on foundational SEO quality by following the best practices enforced by these tools.

🌟 Key Features
The toolkit is comprised of two distinct, powerful Python applications:

1. seo-html-generator.py (The Builder)

This is a Graphical User Interface (GUI) application (using Tkinter) designed to create a perfectly structured, ready-to-use HTML boilerplate with essential SEO metadata.

GUI-Driven: Easy-to-use desktop application for quick generation.

Metadata Control: Allows you to define critical fields like Title, Meta Description, Keywords, and Author.

Save/Load Settings: Ability to save and load your common settings (e.g., site author, general keywords) to a JSON file for rapid deployment across multiple pages.

2. seo-checker.py (The Auditor)

This is a Command-Line Interface (CLI) application that runs a deep technical audit on any given HTML page or live URL. It ensures your page meets the highest quality standards set by search engines.

Dual Source Audit: Check the SEO quality of a local HTML file or a live website URL.

Quality Metrics: Checks against best-practice configurations, including Title character limits (max 60) and Meta Description limits (70-160 characters).

Structured Data Verification: Validates the presence of Schema Markup for types like Article, Product, FAQPage, and more, checking for required properties.

Comprehensive Tag Audit: Scans for a wide range of essential tags, including those related to PWA, Icons, and performance-boosting relations like preload and dns-prefetch.

Remediation Report: Generates a detailed report outlining all issues and suggestions for fixing them.

💻 Installation

The toolkit requires Python 3 to run.

Prerequisites

You need to install the required Python libraries using pip:

pip install requests beautifulsoup4

Note: The tkinter library for the GUI is typically included with standard Python installations on most operating systems.

🚀 Usage

Step 1: Generate Your SEO-Optimized HTML Boilerplate

Use the generator to create a new page foundation or quickly update the metadata for an existing one.

Run the GUI application:

python seo-html-generator.py

A window titled "Penta5W.com SEO HTML Boilerplate Generator (A+ Edition)" will open.

Fill in the required fields (Title, Description, etc.).

Click the Generate HTML button, choose a save location, and the tool will write the highly-optimized .html file.

Step 2: Audit and Validate Your Code

Use the checker to confirm that your newly generated (or existing) HTML file meets the "A=" quality standard.

Run the command-line application:

python seo-checker.py

You will be prompted with a menu:

Choose your audit source:
1. Local File (HTML file on your computer)
2. Web URL (Live website address)
3. Exit

For local files (e.g., the one you just generated): Enter 1, then provide the full file path (e.g., /path/to/my-page.html).

For a live website: Enter 2, then provide the full URL (e.g., https://www.example.com). The script will automatically add the https:// protocol if missing for convenience.

The script will perform a comprehensive audit and save a detailed remediation report to a file in the same directory, guiding you through any required fixes.

🌐 The Complete SEO Toolkit: Go Pro (For Free)
To truly master your SEO and consistently achieve top search rankings, combine the technical foundation provided by this toolkit with the industry-standard analysis tools from Google.

This combination allows you to understand what to fix (from the seo-checker report), how to build it (with the seo-html-generator), and how it is performing in the real world (via Google's platforms).

1. Google Search Console
Purpose: This is your primary tool for monitoring your site's presence in Google Search results.

Submitting Your Content: Ensures Google can find, crawl, and index your pages.

Performance Reports: See which search queries bring users to your site, what your click-through rate (CTR) is, and your average position.

Troubleshooting: Receive alerts for indexing issues, mobile usability problems, and core web vitals errors.

🔗 Access Google Search Console here: https://search.google.com/search-console/about

2. Google Analytics
Purpose: This tool helps you understand user behavior after they click through from the search results to your site.

Behavior Analysis: See how long users stay, which pages they visit, and where they exit.

Conversion Tracking: Measure the impact of your SEO work on your business goals (e.g., purchases, form fills, sign-ups).

Audience Insights: Understand the demographics and technology used by your organic search visitors.

🔗 Access Google Analytics here: https://marketingplatform.google.com/about/analytics/
