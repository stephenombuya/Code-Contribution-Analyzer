# **Code Contribution Analyzer**

**Code Contribution Analyzer** is a powerful tool designed for developers and organizations to analyze and gain insights into their coding contributions across multiple repositories and platforms, including GitHub, GitLab, and Bitbucket. This tool not only provides a breakdown of the number of lines of code written by a user but also groups contributions by programming language and evaluates various projects to deliver meaningful analytics. 

Whether you're an individual developer looking to track your progress or an organization aiming to measure team productivity, Code Contribution Analyzer offers a robust, user-friendly solution to help you manage and understand your coding journey.

---

## Features

### 1. Cross-Platform Repository Analysis
- Connects seamlessly to GitHub, GitLab, and Bitbucket accounts.
- Fetches repositories, including private ones (with proper access permissions).

### 2. Code Contribution Tracking
- Tracks the number of lines of code written by a user since the beginning of their coding journey.
- Categorizes contributions by repository and programming language.

### 3. Programming Language Insights
- Analyzes and visualizes the number of lines written per programming language.
- Helps users identify their most-used languages and areas of expertise.

### 4. Project-Level Analysis
- Provides detailed insights into individual repositories.
- Highlights the largest contributors to each project.
- Tracks code growth over time within specific repositories.

### 5. Visual Reports
- Generates visualizations such as:
  - Pie charts for language distribution.
  - Line graphs for contributions over time.
  - Bar charts for repository-specific contributions.
- Offers downloadable reports in various formats (CSV, JSON, PDF).

### 6. User-Friendly Dashboard
- Interactive and intuitive UI to view analytics.
- Search and filter repositories and contributions for quick insights.

### 7. Authentication & Authorization
- Secure OAuth integration for connecting to code hosting platforms.
- Role-based access control for team collaborations.

### 8. Advanced Search & Filtering
- Search repositories by name, language, or creation date.
- Filter contributions by time period or project.

### 9. Data Export & Backup
- Export analyzed data to formats like CSV, JSON, and PDF for offline analysis.
- Regularly back up insights for future reference.

### 10. Customization Options
- Users can define custom timeframes for contribution tracking.
- Personalize reports with filters and additional metrics.

### 11. Scalability
- Built to handle large datasets, making it ideal for both individuals and large teams.
- Designed with scalability in mind for organizational use.

### 12. API Integration
- Exposes APIs for developers to integrate contribution analytics into other tools or dashboards.
- Facilitates automated tracking and reporting.

---

## Benefits

- **For Individuals:**
  - Monitor your coding journey and identify areas for improvement.
  - Showcase your expertise to potential employers or clients.

- **For Teams:**
  - Assess team productivity and collaboration metrics.
  - Identify the most active contributors and language preferences within the team.

- **For Organizations:**
  - Gain a high-level overview of organizational code contributions.
  - Make data-driven decisions to enhance productivity and workflow.

---

## Technology Stack

- **Backend:** Python (Flask/Django), REST APIs
- **Frontend:** React.js, Bootstrap
- **Database:** PostgreSQL
- **Authentication:** OAuth 2.0
- **Visualization:** Matplotlib, Plotly, or D3.js
- **Deployment:** Docker, AWS/GCP/Azure

---

With Code Contribution Analyzer, you can transform raw contribution data into actionable insights and take your coding journey or team management to the next level.

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
