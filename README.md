# Verra VCS Document Scraper

**Automate your carbon credit research with intelligent web scraping**

A powerful Python-based scraper for the Verra Verified Carbon Standard (VCS) Registry. Extract project summaries, metadata, and document links directly from registry pages. Save hours of manual data collection and transform your carbon credit workflow.

## Why Use This?

Carbon credit research is tedious. Manual browsing of the [Verra VCS Registry](https://registry.verra.org/app/search/VCS) takes time. This scraper eliminates that pain by:

- Extracting complete project summaries and metadata in seconds
- Downloading and organizing all PDF document links automatically
- Handling browser automation, retries, and error recovery for you
- Processing bulk data without manual intervention
- Generating clean CSV reports ready for analysis

Perfect for analysts, investors, carbon compliance teams, and researchers working with VCS projects at scale.

## Quick Start

Install [Taskfile](https://taskfile.dev), a task runner that simplifies command execution:

```bash
task req-install
```

Then run the scraper:

```bash
python3 src/main.py
```

## Usage Options

**Scrape summaries and documents (default)**
```bash
python3 src/main.py
```

**Summaries only (skip document extraction)**
```bash
python3 src/main.py --disable-document
```

**Document links only (skip summaries)**
```bash
python3 src/main.py --disable-summary
```

## Output & Results

The scraper generates two outputs:

**Summary Files**
Text files saved to `results/summary/` named by project ID. Example: `33.txt` contains the summary for VCS project 33.

**Document Index**
A comprehensive CSV file at `results/pdf_links.csv` containing all extracted document metadata, links, and last update timestamps. Use this directly for batch downloading or analysis.

**Visual Reference**
See `docs/assets/verra-scraper-demo.png` for a detailed breakdown of exactly which data the scraper extracts from each registry page.

## Built With

- **Selenium** for reliable browser automation
- **BeautifulSoup** for intelligent HTML parsing
- **Pandas** for clean data transformation
- **Weaviate** for optional vector database integration
- **Python 3.8+** with async task handling

## Features

- Headless Chrome automation for speed and reliability
- Robust error handling and automatic retry logic
- Command-line flexibility for custom scraping workflows
- Clean, organized output structure
- Full metadata preservation
- CSV export ready for downstream analysis

## Performance

Typical scraping speed: 30-60 projects per minute depending on network conditions and document count per project.

## Requirements

- Python 3.8 or higher
- Chrome/Chromium browser
- 2GB RAM minimum
- Active internet connection

## Project Status

Built and maintained by @kspavankrishna. Have feature ideas, bug reports, or improvements? Reach out at kspavankrishna@gmail.com. Contributions, feedback, and collaboration welcome.

## License

Open source and ready to use. See LICENSE for details.

---
