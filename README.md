# Verra VCS Document Scraper

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Selenium 4.0+](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)](https://github.com/kspavankrishna/verra-scaper)

> **Extract verified carbon project data from the Verra Registry in seconds, not hours.** Automate your research workflow with intelligent web scraping powered by Selenium and Python.
>
> *Forked and maintained by @kspavankrishna (kspavankrishna@gmail.com)*

---

## The Problem You're Solving

Working with the Verra Verified Carbon Standard (VCS) Registry means endless manual copying, pasting, and clicking. You need project summaries, PDF documents, metadata, and verification dates. But gathering this from hundreds or thousands of projects is soul-crushing and error-prone.

**Verra VCS Document Scraper eliminates that friction entirely.**

---

## What Makes This Different

This isn't just another web scraper. It's built specifically for the VCS Registry with intelligent automation that handles real-world complications: dynamic page loading, element timeouts, and bulk processing of hundreds of projects without choking your system.

The core engine uses **headless Chrome with Selenium** for reliable, fast extraction. It pulls three critical data points from each project: summary text, document links, and metadata. Then it delivers them in formats you actually want to work with such as clean text files and organized CSV exports.

---

## Key Features

**Intelligent Automation** No more manual registry searches. The scraper reads your input file of project IDs and extracts everything automatically while you focus on analysis.

**Flexible Output Options** Want summaries only? Document links only? Both? Run a single command with optional flags and get exactly what you need.

**Industrial-Strength Reliability** Built-in retry logic, sensible timeouts, and proper error handling mean it keeps working even when the registry hiccups.

**Performance Optimized** Reuses a single browser instance across all projects instead of spinning up and tearing down Chrome for every ID. Processes hundreds of projects in minutes instead of hours.

**Clear Data Organization** Summaries land in `results/summary/` organized by project ID. Document links compile into a single `pdf_links.csv` with metadata and update dates. No mess, no confusion.

---

## Getting Your Hands On It

### Prerequisites

You need [Taskfile](https://taskfile.dev) installed on your system. It's a lightweight task runner that eliminates the need to remember complex command syntax.

### Quick Setup

Clone the repository and install everything in one command:

```bash
git clone https://github.com/kspavankrishna/verra-scaper.git
cd verra-scaper
task req-install
```

This installs all dependencies including Selenium, Pandas, Webdriver Manager, and Loguru.

---

## Running The Scraper

### Default Mode (Summaries + Document Links)

```bash
python3 src/main.py
```

This runs the complete extraction: it grabs project summaries and all associated document links with metadata.

### Summary-Only Mode

```bash
python3 src/main.py --disable-document
```

Get just the text summaries without document link extraction. Faster if you don't need PDFs.

### Document-Links-Only Mode

```bash
python3 src/main.py --disable-summary
```

Extract only the PDF document links and their metadata. Perfect when you already have summaries and need to refresh documents.

---

## Understanding Your Output

**Text Summaries** Each project summary saves as a standalone text file in `results/summary/` with the project ID as the filename. Project 33 becomes `33.txt`. This structure makes it trivial to match summaries back to your original data.

**PDF Links CSV** A single CSV file (`pdf_links.csv`) lands in `results/` containing every document link found across all projects. Each row includes the project ID, document URL, document title, and last update date. Open it in Excel or import into your analysis pipeline.

**Visual Reference** Check `docs/assets/verra-scraper-demo.png` to see exactly which sections of the VCS registry page get extracted. Helps you understand what data you're getting and why.

---

## How The Scraper Works Under The Hood

The tool reads your project ID list, opens a single Chrome browser instance, and navigates through each project page on the VCS registry. For each project it extracts the summary text directly from the page, then crawls through all linked documents to capture URLs and metadata.

It handles authentication, manages page load times intelligently, retries failed extractions, and logs everything so you can debug if needed. When it finishes, it closes the browser cleanly and generates your output files.

---

## Customization & Configuration

Configuration lives in `src/conf_mgr.py`. Default settings include a 10-second element wait timeout and a 2-second inter-project delay to avoid overwhelming the registry servers. Adjust these if you run into timeout issues or want faster processing.

The scraper logs everything to `logs/verra_scraper.log` with automatic rotation when files get large. Check the logs to debug issues or understand what happened during a run.

---

## What You Can Build With This

Researchers and analysts use this scraper to build verified carbon credit databases, run comparative analysis across projects, track document changes over time, or feed clean project data into machine learning pipelines. Organizations conducting due diligence on carbon projects save days of manual work.

---

## Contributing

Found a bug or have an idea? Contributions are welcome. Check the repository issues, fork the code, make your improvements, and open a pull request. This tool works best when the community helps shape it. Want to collaborate or suggest improvements? Contact @kspavankrishna at kspavankrishna@gmail.com.

---

## Technical Stack

Built on proven technologies: **Python 3.10+** for core logic, **Selenium 4.0+** for browser automation, **Pandas** for data handling, **Loguru** for structured logging, and **Webdriver Manager** for automatic driver management.

---

## License

 Apache-2.0 license
 
---

## Need Help?

If you hit issues, check your logs first (`logs/verra_scraper.log`). The scraper logs what it's doing at each step. For configuration questions, review `src/conf_mgr.py`. For technical questions or custom implementations, reach out to @kspavankrishna at kspavankrishna@gmail.com or open an issue on GitHub.

**Pro tip**: Looking for advanced features or custom scraping logic? @kspavankrishna specializes in carbon data extraction and registry automation. Drop a line at kspavankrishna@gmail.com.

---

**Made for people who want to work with carbon data, not waste time gathering it.**
