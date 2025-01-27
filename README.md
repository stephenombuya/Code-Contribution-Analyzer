# **Code Contribution Analyzer**

## **Root Directory Structure**
```
code-contribution-analyzer/
├── src/                         # Main application source code
│   ├── api_clients/             # Modules for interacting with GitHub, GitLab, and Bitbucket APIs
│   │   ├── github_client.py     # GitHub API interaction logic
│   │   ├── gitlab_client.py     # GitLab API interaction logic
│   │   ├── bitbucket_client.py  # Bitbucket API interaction logic
│   │   └── base_client.py       # Shared base class for API clients
│   ├── analysis/                # Core logic for analyzing code and repositories
│   │   ├── repo_fetcher.py      # Logic to fetch repositories (clone/download)
│   │   ├── line_counter.py      # Line count logic per file
│   │   ├── language_detector.py # Detect programming languages using extensions or metadata
│   │   └── contribution_analyzer.py # Logic to attribute contributions (e.g., git blame)
│   ├── visualization/           # Data visualization and reporting tools
│   │   ├── charts.py            # Generate graphs and visualizations (e.g., LOC by language)
│   │   ├── report_generator.py  # Generate reports in various formats (JSON, CSV, PDF)
│   │   └── export_handler.py    # Export data to files or dashboards
│   ├── utils/                   # Helper functions and shared utilities
│   │   ├── config_loader.py     # Load configuration from .env or JSON files
│   │   ├── logging_handler.py   # Logging setup for the tool
│   │   └── rate_limiter.py      # Handle API rate limits and retries
│   ├── cli/                     # Command-line interface logic
│   │   ├── argument_parser.py   # Parse CLI arguments
│   │   └── cli_runner.py        # Entry point for CLI
│   ├── web/                     # Web-based interface (optional)
│   │   ├── app.py               # Flask/Django app entry point
│   │   ├── templates/           # HTML templates for web interface
│   │   └── static/              # Static assets (CSS, JS, images)
│   └── main.py                  # Main entry point for the tool
├── tests/                       # Unit and integration tests
│   ├── test_api_clients.py      # Test cases for API clients
│   ├── test_analysis.py         # Test cases for analysis functions
│   ├── test_visualization.py    # Test cases for visualization and reporting
│   └── test_cli.py              # Test cases for the CLI
├── data/                        # Temporary storage for cloned repositories and reports
│   ├── repos/                   # Cloned repositories
│   └── reports/                 # Generated reports (CSV, JSON, PDF, etc.)
├── .env                         # Environment variables (e.g., API keys, secrets)
├── requirements.txt             # Python dependencies
├── CODE_OF_CONDUCT.md           # For ensuring utmost standards of professionalism are upheld
├── CONTRIBUTING.md              # Guidelines to be followed when contributing to the project
├── README.md                    # Project documentation
├── LICENSE                      # License for the project
├── setup.py                     # Packaging and installation configuration
└── .gitignore                   # Ignored files and folders (e.g., API keys, data folders)
```

---

# **README.md**

```markdown
# Code Contribution Analyzer

**A powerful tool for analyzing your coding contributions across GitHub, GitLab, and Bitbucket. Track the number of lines you've written, group by programming language, analyze projects, and gain insights into your coding journey!**

## Features

- Fetch repositories from GitHub, GitLab, and Bitbucket using APIs.
- Count lines of code (LOC) and group by programming language.
- Summarize contributions per project or overall.
- Analyze individual contributions using `git blame` and `git log`.
- Generate detailed reports with charts and export them to CSV, JSON, or PDF.
- Optional web-based interface for interactive analysis.
- CLI for quick, command-line-driven insights.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/stephenombuya/Code-Contribution-Analyzer
   cd code-contribution-analyzer
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - Create a `.env` file in the root directory and add the following:
     ```env
     GITHUB_API_KEY=<your_github_api_key>
     GITLAB_API_KEY=<your_gitlab_api_key>
     BITBUCKET_API_KEY=<your_bitbucket_api_key>
     ```

4. Run the tool:
   ```bash
   python src/main.py
   ```

## Usage

### CLI Mode
Use the command-line interface for quick analysis:
```bash
python src/main.py --platform github --username your-username --analyze
```

### Web Interface (Optional)
Run the Flask/Django app for an interactive dashboard:
```bash
python src/web/app.py
```
Then, navigate to `http://127.0.0.1:5000` in your browser.

## Example Outputs

- **Programming Language Breakdown**:
  ![Example Chart](docs/images/language_breakdown.png)

- **Overall Contributions Report**:
  ```
  Total Repositories: 42
  Total Lines of Code: 1,245,672
  Languages: Python (500,000), JavaScript (300,000), Java (200,000), C++ (145,672), Others (100,000)
  ```

## Roadmap

- Support for additional version control platforms (e.g., Azure DevOps).
- Add features for team-level analysis.
- Integrate AI-driven insights for productivity tracking.
- Enhance visualizations with more detailed charts.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Developed with ❤️ by [Stephen Ombuya](https://github.com/stephenombuya).
