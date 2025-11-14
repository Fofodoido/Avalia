# Agile Practices Quality Evaluator v4.0

An advanced tool for evaluating agile software development practices in GitHub organizations using both quantitative metrics and AI-powered qualitative analysis.

## Overview

This tool analyzes GitHub repositories and contributors to assess the quality of agile development practices. It combines traditional metrics (commits, issues, PRs, code reviews) with AI-powered analysis of commit messages, issue descriptions, and code review quality to provide comprehensive agile maturity scoring.

## Key Features

### 🔍 **Comprehensive Analysis**
- **Repository Signals**: README, license, CI/CD, tests, documentation
- **Contribution Metrics**: Commits, issues, pull requests, comments
- **Quality Assessment**: Mature issues/PRs, atomic commits, diversity metrics
- **Team Dynamics**: Weekly activity patterns, collaboration indicators

### 🤖 **AI-Powered Quality Analysis** (New in v4.0)
- **Commit Message Quality**: Evaluates clarity, conventional commits, atomic changes
- **Issue/Story Quality**: Assesses acceptance criteria, user story format, testability
- **Code Review Quality**: Analyzes constructiveness, specificity, collaborative tone
- **Smart Recommendations**: Personalized improvement suggestions

### 📊 **Multi-Level Scoring**
- **Individual Scores**: Per-user agile maturity assessment
- **Repository Details**: Granular metrics per repo per user
- **Organizational Overview**: Team-wide patterns and trends

## Installation

### Prerequisites
- Python 3.8+
- GitHub API access token
- OpenAI API key (optional, for AI features)

### Setup
```bash
# Clone or download the project
cd revisao-mds

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
# Edit .env with your tokens
```

### Environment Configuration
Create a `.env` file with your API keys:
```bash
# GitHub token (required)
GH_TOKEN=github_pat_your_token_here

# OpenAI API key (optional, for AI analysis)
OPENAI_API_KEY=sk-proj-your_key_here
```

## Usage

### Basic Usage
```bash
# Analyze organization since specific date
python aval-mds.py --org your-org --since 2024-08-01 --out results.xlsx

# With AI analysis enabled
python aval-mds.py --org your-org --since 2024-08-01 --out results.xlsx

# Without AI analysis (faster, lower cost)
python aval-mds.py --org your-org --since 2024-08-01 --out results.xlsx --disable-ai
```

### Advanced Options
```bash
# Filter to recent repositories only
python aval-mds.py --org your-org --since 2024-08-01 --only-recent --skip-forks

# Analyze specific users
python aval-mds.py --org your-org --since 2024-08-01 --users-csv users.csv

# Adjust performance
python aval-mds.py --org your-org --since 2024-08-01 --workers 4

# Debug authentication issues
python aval-mds.py --org your-org --since 2024-08-01 --debug-auth
```

### Command Line Arguments
| Argument | Description | Required |
|----------|-------------|----------|
| `--org` | GitHub organization name | ✅ |
| `--since` | Start date (YYYY-MM-DD) | ✅ |
| `--out` | Output Excel file | No (default: avaliacao.xlsx) |
| `--token` | GitHub token (or use GH_TOKEN env) | No |
| `--openai-key` | OpenAI key (or use OPENAI_API_KEY env) | No |
| `--disable-ai` | Disable AI analysis | No |
| `--workers` | Concurrent workers | No (default: 8) |
| `--skip-forks` | Skip forked repositories | No |
| `--only-recent` | Skip repos with old activity | No |
| `--users-csv` | CSV file with github_username column | No |
| `--debug-auth` | Show authentication diagnostics | No |

## Output Format

The tool generates an Excel file with three sheets:

### 1. **Resumo_por_usuario** (User Summary)
Per-user aggregated scores and metrics:
- `github_username`: User identifier
- `score_final_0_1`: Overall agile maturity score (0.0-1.0)
- `nivel`: Maturity level (Maduro/Saudável/Iniciante)
- `commits_total`, `issues_total`, `prs_total`: Activity counts
- `mature_issues_total`, `mature_prs_total`: Quality indicators
- `atomicity_media`: Average commit atomicity
- `ai_commit_quality_media`: AI-assessed commit message quality
- `ai_issue_quality_media`: AI-assessed issue/story quality
- `ai_review_quality_media`: AI-assessed code review quality

### 2. **Detalhes_por_repo** (Repository Details)
Per-user per-repository detailed metrics:
- Repository metadata (name, language, stars, etc.)
- Individual contribution counts
- Repository quality signals (README, tests, CI/CD, etc.)
- Detailed scoring components
- AI quality assessments per repository

### 3. **Proveniencia** (Provenance)
Analysis metadata:
- Organization and date range
- Configuration parameters
- Scoring weights and targets
- Generation timestamp

## Scoring Methodology

### Core Metrics (Traditional)
- **Weekly Activity**: Consistent commits, issues, PRs, comments
- **Quality Indicators**: Mature issues/PRs with proper discussion
- **Technical Practices**: Atomic commits, diverse issue types
- **Repository Health**: Documentation, tests, CI/CD setup

### AI-Enhanced Metrics (New)
- **Commit Quality**: Clarity, conventional format, atomic changes
- **Issue Quality**: Acceptance criteria, user story format, testability
- **Review Quality**: Constructive feedback, specific suggestions

### Maturity Levels
- **Maduro** (≥75%): Excellent agile practices
- **Saudável** (45-74%): Good practices with room for improvement  
- **Iniciante** (<45%): Basic practices, needs development

## AI Analysis Details

### Commit Message Analysis
Evaluates based on:
- **Clarity**: Clear, descriptive messages
- **Specificity**: Detailed what/why information
- **Conventional Commits**: Following standard formats
- **Atomicity**: Single-purpose changes

### Issue/Story Analysis
Assesses:
- **Acceptance Criteria**: Clear, testable requirements
- **User Story Format**: Proper "As a... I want... So that..." structure
- **Sufficient Detail**: Complete context and requirements
- **Testability**: Verifiable completion criteria

### Code Review Analysis
Examines:
- **Constructiveness**: Helpful, actionable feedback
- **Specificity**: Detailed suggestions and explanations
- **Coverage**: Addresses quality, security, performance
- **Collaboration**: Professional, supportive tone

## GitHub Token Requirements

### Fine-Grained Token (Recommended)
- **Resource Owner**: Target organization
- **Repository Access**: All repositories to analyze
- **Permissions (Read)**: Contents, Metadata, Issues, Pull Requests, Members
- **SSO**: Must be authorized for the organization

### Classic Token
- **Scopes**: `repo`, `read:org`
- **SSO**: Must be authorized for the organization

## Performance and Rate Limiting

The tool is designed to be GitHub API rate-limit friendly:
- Automatic rate limit monitoring and waiting
- Configurable worker count for parallel processing
- Built-in delays to prevent API abuse
- Smart sampling for AI analysis to control costs

### Optimization Tips
- Use `--only-recent` for faster analysis
- Use `--skip-forks` to focus on original repositories
- Reduce `--workers` if hitting rate limits
- Use `--disable-ai` for faster runs without AI costs

## Troubleshooting

### Authentication Issues
```bash
# Test your token
curl -H "Authorization: Bearer $GH_TOKEN" https://api.github.com/user

# Debug authentication
python aval-mds.py --org your-org --since 2024-01-01 --debug-auth
```

### Common Issues
- **401 Unauthorized**: Check token validity and SSO authorization
- **PaginatedList errors**: Fixed in v4.0 with safe iteration
- **Empty results**: Verify date range and repository activity
- **AI errors**: Check OpenAI API key and quota

## Architecture

### Core Components
- **`AgileQualityAnalyzer`**: AI-powered quality assessment
- **`collect_repo_contrib()`**: Data collection from GitHub API
- **`build_user_scorer()`**: Scoring algorithm implementation
- **Rate limiting and error handling**: Robust API interaction

### Data Flow
1. **Authentication**: Verify GitHub and OpenAI access
2. **Repository Discovery**: Find organization repositories
3. **Data Collection**: Gather commits, issues, PRs, comments
4. **AI Analysis**: Assess quality using OpenAI (optional)
5. **Scoring**: Calculate agile maturity metrics
6. **Output Generation**: Create Excel report

## Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug output
python aval-mds.py --org test-org --since 2024-01-01 --debug-auth
```

### Configuration
Scoring weights can be adjusted in `CRITERIA_WEIGHTS`:
```python
CRITERIA_WEIGHTS = {
    "weekly_commits": 0.08,
    "ai_commit_quality": 0.08,
    "ai_issue_quality": 0.08,
    # ... other weights
}
```

## License

This tool is designed for educational and research purposes in software engineering and agile methodology assessment.

## Version History

- **v4.0**: Added AI-powered quality analysis with OpenAI integration
- **v3.2**: Enhanced rate limiting and authentication diagnostics
- **v3.1**: Improved criteria weighting and stability metrics
- **v3.0**: Multi-threaded processing and comprehensive scoring

## Support

For issues and questions:
1. Check the troubleshooting section
2. Verify your GitHub token permissions
3. Test with a smaller date range or user set
4. Review the debug output with `--debug-auth`
