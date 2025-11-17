# 💼 AI Accountant Chatbot

An intelligent chatbot that analyzes financial statements (Balance Sheets and P&L statements) using Google's Gemini AI with code execution capabilities.

## Features

- 📊 **Automatic Statement Recognition**: Identifies whether uploaded files are Balance Sheets or P&L statements
- 🤖 **AI-Powered Analysis**: Uses Gemini 2.5 Pro with code execution for accurate financial calculations
- 💬 **Natural Language Queries**: Ask questions about your financial data in plain English
- 📁 **Excel Support**: Upload financial statements in Excel format (.xlsx, .xls)
- 🔍 **Multi-Period Support**: Handles Balance Sheets with multiple time periods

## Local Development

### Prerequisites

- Python 3.12.12
- Gemini API Key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/vwake09/limo_demo.git
cd limo_demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create your secrets file:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

4. Edit `.streamlit/secrets.toml` and add your Gemini API key:
```toml
GEMINI_API_KEY = "your-actual-api-key-here"
```

5. Run the app:
```bash
streamlit run streamlit_app.py
```

## Deployment to Streamlit Cloud

### Step 1: Push to GitHub

Your code is already on GitHub at: `https://github.com/vwake09/limo_demo`

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select:
   - **Repository**: `vwake09/limo_demo`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
5. Click "Advanced settings"
6. Set **Python version**: `3.12`
7. Under **Secrets**, add your API key:
```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
```
8. Click "Deploy"!

Your app will be live at: `https://[your-app-name].streamlit.app`

## Usage

1. **Upload Financial Statements**:
   - Use the sidebar to upload your Balance Sheet and/or P&L statement (Excel format)
   - The app will automatically identify the statement type

2. **Ask Questions**:
   - Type natural language questions in the chat input
   - Examples:
     - "What was the total revenue?"
     - "Show me the checking account balance for April 2025"
     - "What's the net income for this period?"
     - "Compare assets between Jan and March"

3. **View Code**:
   - Click "View Generated Code" to see the Python code Gemini used to calculate the answer

## Tech Stack

- **Streamlit**: Web application framework
- **Google Gemini 2.5 Pro**: AI model with code execution
- **Pydantic**: Data validation and schema enforcement
- **Pandas**: Data processing
- **openpyxl**: Excel file handling

## Security Note

⚠️ **Never commit your API keys to version control!** Always use Streamlit secrets for sensitive information.

## License

MIT License

## Author

Built with ❤️ using Streamlit and Google Gemini

