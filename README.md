# Verra VCS Document Scraper

This tool scrapes document data from the Verra Verified Carbon Standard (VCS) Registry, pulling summaries, metadata, and PDF document links directly from project pages. If you work with carbon credits, this saves hours of manual data gathering from the registry.

You can explore the registry yourself at [Verra VCS Registry](https://registry.verra.org/app/search/VCS).

## What It Does

The scraper automates the extraction of summary text and document information from VCS projects. It gives you a simple command-line interface to customize what you want to grab, whether that's just summaries, just document links, or both. It handles the browser automation, error recovery, and file management so you don't have to.

## Getting Started

You'll need Taskfile installed on your system. [Taskfile](https://taskfile.dev) is a task runner that makes it easy to execute predefined tasks without remembering complex commands.

Once you have Taskfile set up, install all dependencies by running:

```bash
task req-install
```

## Using the Scraper

To run the full scrape of both summary data and PDF links, execute:

```bash
python3 src/main.py
```

If you only want summaries without the document links, pass the flag:

```bash
python3 src/main.py --disable-document
```

If you only want the PDF links without summaries:

```bash
python3 src/main.py --disable-summary
```

## What You Get

Summary text files go into `results/summary` with filenames matching the project ID (like `33.txt` for project 33). All the document links, along with their metadata and last update dates, get compiled into a single CSV file called `pdf_links.csv` in the `results/` directory. You can use those CSV links to download documents directly.

The image in `docs/assets/verra-scraper-demo.png` shows exactly which parts of the VCS registry page the scraper pulls from, so you know what data you're getting.

---
