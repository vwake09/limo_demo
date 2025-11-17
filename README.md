# 💼 AI Accountant Chatbot - Intelligent Financial Statement Analysis

An advanced AI-powered chatbot that automatically parses, understands, and analyzes financial statements using Google's Gemini 2.5 Pro with code execution capabilities. Upload your Excel files and ask natural language questions to get instant, accurate financial insights.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Use Case & Problem Statement

### The Challenge
Financial professionals, accountants, and business owners regularly need to:
- Extract specific information from financial statements quickly
- Compare values across multiple time periods
- Perform calculations and financial ratio analysis
- Answer ad-hoc questions about financial data without manual spreadsheet manipulation


### The Solution
This AI Accountant Chatbot revolutionizes financial data analysis by:
- ✅ **Automatically identifying** statement types (P&L or Balance Sheet)
- ✅ **Intelligently parsing** complex Excel formats with varying structures
- ✅ **Understanding natural language** questions in plain English
- ✅ **Executing Python code** to perform accurate calculations
- ✅ **Supporting multi-period** analysis for Balance Sheets
- ✅ **Providing transparent answers** with viewable code execution

---

## 🌟 Key Features

### 1. 🤖 Intelligent Statement Recognition
Automatically detects whether uploaded files are:
- **Profit & Loss (P&L) Statements**: Income, expenses, COGS, net income
- **Balance Sheets**: Assets, liabilities, equity across multiple periods

### 2. 📊 Advanced Parsing Capabilities
- **Multi-period support**: Handles Balance Sheets with multiple time columns (Jan, Feb, Mar, etc.)
- **Flexible formats**: Adapts to different Excel layouts and structures
- **Nested categories**: Understands parent-child account relationships
- **Null handling**: Gracefully manages missing or empty values

### 3. 💬 Natural Language Query Interface
Ask questions in plain English:
- "What was the total revenue for this period?"
- "Show me the checking account balance in April 2025"
- "What's the difference between total assets in January and March?"
- "Calculate the current ratio"
- "What percentage of total expenses was spent on salaries?"

### 4. 🔍 Transparent AI Execution
- **View generated code**: See exactly how Gemini calculates each answer
- **Code execution**: Leverages Gemini's built-in Python code execution
- **Validated schemas**: Uses Pydantic for data validation and type safety

### 5. 📁 User-Friendly Interface
- **Drag-and-drop uploads**: Simple Excel file upload (.xlsx, .xls)
- **Real-time processing**: Instant statement parsing and analysis
- **Chat history**: Maintains conversation context
- **Status indicators**: Clear feedback on loaded statements
- **Reset functionality**: Start fresh anytime

---

## 🏗️ Architecture & Technical Design

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  (File Upload, Chat Interface, Status Display)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  AccountantChatbot Class                     │
│  • Manages P&L and Balance Sheet data                       │
│  • Coordinates parsing and query processing                 │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ↓                             ↓
┌──────────────────────┐    ┌──────────────────────┐
│  Document Parsing    │    │  Query Processing    │
│  • Excel → CSV       │    │  • Context Building  │
│  • Type Detection    │    │  • Code Execution    │
│  • Schema Extraction │    │  • Answer Formatting │
└──────────┬───────────┘    └──────────┬───────────┘
           │                           │
           └────────────┬──────────────┘
                        ↓
           ┌─────────────────────────┐
           │   Google Gemini 2.5 Pro │
           │   • JSON Schema Output  │
           │   • Code Execution      │
           │   • Natural Language    │
           └─────────────────────────┘
```

### Data Flow

1. **Upload Phase**:
   ```
   Excel File → Pandas → CSV String → Gemini API → Type Identification
                                                   ↓
   Statement Type Detected → Specific Parser (P&L or Balance Sheet)
                                                   ↓
   Structured JSON → Pydantic Validation → Stored in Session
   ```

2. **Query Phase**:
   ```
   User Question → Context Builder (with stored data)
                                    ↓
   Gemini API with Code Execution → Python Code Generated
                                    ↓
   Code Executed → Results Extracted → Natural Language Answer
   ```

### Schema Design

#### Profit & Loss Schema
```python
{
  "statement_type": "profit_and_loss",
  "company_name": "ABC Corp",
  "period_start": "2025-01-01",
  "period_end": "2025-03-31",
  "income_items": [...],      # Revenue line items
  "expense_items": [...],     # Expense line items
  "cogs_items": [...],        # Cost of goods sold
  "total_income": 150000.00,
  "total_expenses": 85000.00,
  "net_income": 65000.00
}
```

#### Balance Sheet Schema
```python
{
  "statement_type": "balance_sheet",
  "time_periods": ["Jan 2025", "Feb 2025", "Mar 2025"],
  "assets": {
    "Checking": {
      "Jan 2025": 4875.00,
      "Feb 2025": 4570.45,
      "Mar 2025": 4321.40
    },
    ...
  },
  "liabilities": {...},
  "equity": {...}
}
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12.12
- Gemini API Key ([Get it here](https://makersuite.google.com/app/apikey))
- Excel files with financial statements

### Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vwake09/limo_demo.git
   cd limo_demo
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure secrets**:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   
   Edit `.streamlit/secrets.toml` and add your API key:
   ```toml
   GEMINI_API_KEY = "your-actual-api-key-here"
   ```

4. **Run the application**:
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser** to `http://localhost:8501`

---

## ☁️ Deployment to Streamlit Cloud

### Step-by-Step Deployment

1. **Visit Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with your GitHub account

2. **Create New App**:
   - Click "New app"
   - Select repository: `vwake09/limo_demo`
   - Branch: `main`
   - Main file path: `streamlit_app.py`

3. **Configure Settings**:
   - Click "Advanced settings"
   - Python version: `3.12`

4. **Add Secrets**:
   In the Secrets section, add:
   ```toml
   GEMINI_API_KEY = "your-gemini-api-key-here"
   ```

5. **Deploy**:
   - Click "Deploy!"
   - Wait 2-3 minutes for deployment
   - Your app will be live at: `https://[your-app-name].streamlit.app`

---

## 📖 Usage Guide

### 1. Upload Financial Statements

**Balance Sheet**:
- Use the sidebar uploader labeled "Upload Balance Sheet"
- Supported formats: `.xlsx`, `.xls`
- Can contain multiple time periods as columns

**Profit & Loss Statement**:
- Use the sidebar uploader labeled "Upload P&L Statement"
- Supported formats: `.xlsx`, `.xls`
- Typically shows a single period or comparison periods

### 2. Ask Questions

Once files are uploaded, you can ask questions like:

**Basic Queries**:
- "What is the net income?"
- "Show me total assets"
- "What's the checking account balance?"

**Time-based Queries** (for Balance Sheets):
- "What was the checking balance in January 2025?"
- "Show me savings account values for all periods"
- "Compare total assets between January and March"

**Calculations**:
- "Calculate total income minus total expenses"
- "What percentage of expenses was spent on rent?"
- "What's the current ratio?" (Current Assets / Current Liabilities)
- "Calculate the debt-to-equity ratio"

**Comparisons**:
- "How much did total assets grow from Jan to Mar?"
- "What's the month-over-month change in liabilities?"
- "Which expense category had the highest cost?"

### 3. View Generated Code

For transparency and debugging:
- Click "View Generated Code" in any AI response
- See the exact Python code Gemini used for calculations
- Verify the logic and results

### 4. Reset and Start Fresh

- Click the "Reset All" button in the sidebar
- Clears all uploaded data and chat history
- Upload new files and start a new session

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Web UI, file uploads, chat interface |
| **AI Model** | Google Gemini 2.5 Pro | Document parsing, code execution, NLU |
| **Data Validation** | Pydantic | Schema validation, type safety |
| **Data Processing** | Pandas | Excel to CSV conversion |
| **Excel Handling** | openpyxl | Reading Excel files |
| **Language** | Python 3.12 | Core application logic |

### Why These Technologies?

- **Streamlit**: Rapid development, built-in file upload, chat interface components
- **Gemini 2.5 Pro**: Advanced reasoning, JSON schema output, Python code execution
- **Pydantic**: Runtime type checking, data validation, automatic documentation
- **Pandas**: Industry-standard for data manipulation and Excel file handling

---

## 🔒 Security & Privacy

### API Key Management
- ✅ API keys stored in Streamlit secrets (not in code)
- ✅ `.streamlit/secrets.toml` is git-ignored
- ✅ Example template provided for easy setup
- ⚠️ **Never commit secrets.toml to version control**

### Data Privacy
- 📄 Files are processed in memory only
- 🔄 Data sent to Google's Gemini API for processing
- 🗑️ No persistent storage of financial data
- 🔒 Session data cleared on browser refresh or reset

### Best Practices
1. Keep your Gemini API key confidential
2. Don't share your deployed app URL publicly if it contains sensitive data
3. Use Streamlit Cloud's authentication if needed
4. Regularly rotate API keys
5. Monitor API usage and set billing alerts

---

## 📊 Example Use Cases

### Use Case 1: Monthly Financial Review
**Scenario**: A small business owner wants to review financial health

**Actions**:
1. Upload Balance Sheet with Jan-Mar 2025 data
2. Upload P&L for Q1 2025
3. Ask: "What's the trend in cash balances?"
4. Ask: "Is revenue growing faster than expenses?"
5. Ask: "Calculate my quick ratio"

**Result**: Instant insights without Excel formulas or manual calculations

### Use Case 2: Investor Due Diligence
**Scenario**: An investor analyzing a company's financials

**Actions**:
1. Upload multiple periods of financial statements
2. Ask: "What's the debt-to-equity ratio?"
3. Ask: "How has working capital changed?"
4. Ask: "Show me the gross profit margin"

**Result**: Quick financial ratio analysis for investment decisions

### Use Case 3: Accountant's Assistant
**Scenario**: An accountant preparing client reports

**Actions**:
1. Upload client's Balance Sheet and P&L
2. Ask: "List all accounts with negative balances"
3. Ask: "What's the total depreciation expense?"
4. Ask: "Compare this quarter's revenue to expenses"

**Result**: Fast data extraction for report preparation

---

## 🧪 Example Questions

### For Balance Sheets:
```
✓ "What's the total of all bank accounts in March 2025?"
✓ "Show me the trend in total assets from Jan to Mar"
✓ "What percentage of total assets is cash?"
✓ "Calculate the current ratio for February"
✓ "Which asset account has the highest value?"
✓ "How much did total equity change from January to March?"
```

### For P&L Statements:
```
✓ "What was the gross profit for this period?"
✓ "List all expense categories above $5,000"
✓ "What percentage of revenue is net income?"
✓ "Calculate operating margin"
✓ "What's the total of all income items?"
✓ "Compare COGS to total expenses"
```

---

## 🐛 Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found"**:
- Ensure secrets.toml exists in `.streamlit/` folder
- Verify the key is correctly formatted: `GEMINI_API_KEY = "your-key"`
- For Streamlit Cloud: Check secrets in app settings

**File Upload Fails**:
- Ensure file is `.xlsx` or `.xls` format
- Check that the file contains recognizable financial data
- Try simplifying complex spreadsheet formatting

**Statement Not Recognized**:
- Verify the statement has clear headers (Income, Assets, etc.)
- Ensure there's financial data in the spreadsheet
- Check that the file isn't password-protected

**Slow Response Times**:
- Large files take longer to process
- First query after upload is slower (parsing phase)
- Subsequent queries are faster (data is cached)

---

## 🗺️ Roadmap & Future Enhancements

### Planned Features
- [ ] Multi-file comparison (compare financial statements from different companies)
- [ ] Export analysis results to PDF reports
- [ ] Financial ratio dashboard with visualizations
- [ ] Support for Cash Flow Statements
- [ ] Historical trend analysis across multiple periods
- [ ] Budget vs. Actual comparisons
- [ ] Automated anomaly detection
- [ ] Support for additional file formats (CSV, PDF)
- [ ] Custom schema definitions for specialized statements
- [ ] Multi-language support

### Potential Integrations
- QuickBooks API integration
- Xero API integration
- Google Sheets import
- Automated email reports

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions
- Update README for new features
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Vivek Singh** (vwake09)
- GitHub: [@vwake09](https://github.com/vwake09)

Built with ❤️ using Streamlit and Google Gemini

---

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing web framework
- [Google Gemini](https://deepmind.google/technologies/gemini/) for powerful AI capabilities
- [Pydantic](https://docs.pydantic.dev/) for robust data validation
- The open-source community for inspiration and tools

---

## 📞 Support

If you encounter issues or have questions:
- 🐛 [Open an issue](https://github.com/vwake09/limo_demo/issues)
- 💬 Start a discussion in the repository
- 📧 Contact the maintainer

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with Streamlit | Powered by Google Gemini 2.5 Pro**
