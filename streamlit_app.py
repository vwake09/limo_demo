# ==================== INSTALLATION ====================
# !pip install google-genai pandas openpyxl pydantic streamlit

import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import List, Optional, Literal, Dict
import json
import warnings
import io

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# ==================== CONFIGURATION ====================
# Get API key from Streamlit secrets
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("⚠️ GEMINI_API_KEY not found in secrets. Please configure it in Streamlit Cloud settings.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

# ==================== PYDANTIC SCHEMAS ====================
class StatementIdentification(BaseModel):
    statement_type: Literal["profit_and_loss", "balance_sheet", "unknown"]
    confidence: float
    reasoning: str

class LineItem(BaseModel):
    display_name: str
    value: Optional[float]
    period: Optional[str]
    parent_category: Optional[str]

class ProfitAndLossSchema(BaseModel):
    statement_type: str
    company_name: Optional[str]
    period_start: Optional[str]
    period_end: Optional[str]
    income_items: List[LineItem]
    expense_items: List[LineItem]
    cogs_items: List[LineItem]
    gross_profit: Optional[float]
    net_income: Optional[float]
    total_income: Optional[float]
    total_expenses: Optional[float]

class BalanceSheetSchemaRaw(BaseModel):
    """List-based Balance Sheet Schema - VALIDATED by Gemini"""
    statement_type: str
    company_name: Optional[str]
    as_of_date: Optional[str]
    time_periods: List[str]
    asset_items: List[LineItem]
    liability_items: List[LineItem]
    equity_items: List[LineItem]
    total_assets: Optional[List[float]]
    total_liabilities: Optional[List[float]]
    total_equity: Optional[List[float]]

class BalanceSheetSchema(BaseModel):
    """Dict-based Balance Sheet Schema - for storage after transformation"""
    statement_type: str
    company_name: Optional[str]
    as_of_date: Optional[str]
    time_periods: List[str]
    assets: Dict[str, Dict[str, Optional[float]]]
    liabilities: Dict[str, Dict[str, Optional[float]]]
    equity: Dict[str, Dict[str, Optional[float]]]
    total_assets: Optional[Dict[str, Optional[float]]]
    total_liabilities: Optional[Dict[str, Optional[float]]]
    total_equity: Optional[Dict[str, Optional[float]]]

# ==================== HELPER FUNCTIONS ====================
def balance_sheet_to_dict(raw_bs: BalanceSheetSchemaRaw) -> BalanceSheetSchema:
    """Transform validated list structure to dict for easy querying"""
    
    def items_to_dict(items: List[LineItem]) -> Dict[str, Dict[str, Optional[float]]]:
        result = {}
        for item in items:
            if item.display_name not in result:
                result[item.display_name] = {}
            if item.period:
                result[item.display_name][item.period] = item.value
        return result
    
    def list_to_period_dict(values: Optional[List[float]], periods: List[str]) -> Optional[Dict[str, Optional[float]]]:
        if values is None:
            return None
        return dict(zip(periods, values))
    
    return BalanceSheetSchema(
        statement_type=raw_bs.statement_type,
        company_name=raw_bs.company_name,
        as_of_date=raw_bs.as_of_date,
        time_periods=raw_bs.time_periods,
        assets=items_to_dict(raw_bs.asset_items),
        liabilities=items_to_dict(raw_bs.liability_items),
        equity=items_to_dict(raw_bs.equity_items),
        total_assets=list_to_period_dict(raw_bs.total_assets, raw_bs.time_periods),
        total_liabilities=list_to_period_dict(raw_bs.total_liabilities, raw_bs.time_periods),
        total_equity=list_to_period_dict(raw_bs.total_equity, raw_bs.time_periods)
    )

# ==================== PARSING FUNCTIONS ====================
def excel_to_csv_string(file_path_or_bytes) -> str:
    """Convert Excel to CSV string"""
    if isinstance(file_path_or_bytes, str):
        df = pd.read_excel(file_path_or_bytes, header=None)
    else:
        df = pd.read_excel(file_path_or_bytes, header=None)
    return df.to_csv(header=False, index=False)

def identify_statement_type(csv_content: str) -> StatementIdentification:
    """Identify if statement is P&L or Balance Sheet"""
    prompt = f"""Analyze this financial statement and determine if it's a Profit & Loss (P&L) or Balance Sheet.

CSV Content:
{csv_content}

Look for indicators:
- P&L: Income, Revenue, Expenses, Net Income, COGS
- Balance Sheet: Assets, Liabilities, Equity, as of [date]

Provide:
- statement_type: one of "profit_and_loss", "balance_sheet", or "unknown"
- confidence: a number between 0 and 1
- reasoning: explanation of your decision

Return your analysis as JSON."""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=StatementIdentification,
            max_output_tokens=32000
        )
    )
    return StatementIdentification.model_validate_json(response.text)

def parse_profit_loss(csv_content: str) -> ProfitAndLossSchema:
    """Parse P&L statement using Gemini"""
    prompt = f"""Parse this Profit & Loss statement into structured JSON.

CSV Content:
{csv_content}

IMPORTANT INSTRUCTIONS:
1. Extract the PERIOD INFORMATION from the statement header
2. For each line item, extract the TOTAL value for the period
3. Most P&L statements show TOTALS for the entire period

Extract ALL of the following:
- statement_type: set to "profit_and_loss"
- company_name: company name if available (null if not found)
- period_start: start date of the reporting period (null if not found)
- period_end: end date of the reporting period (null if not found)
- income_items: list of all income/revenue line items with display_name and value
- expense_items: list of all expense line items with display_name and value
- cogs_items: list of all COGS line items with display_name and value
- gross_profit: gross profit total (null if not found)
- net_income: net income total (null if not found)
- total_income: total income (null if not found)
- total_expenses: total expenses (null if not found)

For line items:
- display_name: the account name
- value: the monetary amount for the TOTAL PERIOD (null if not found)
- period: ONLY populate if the statement shows MULTIPLE time period columns (null otherwise)
- parent_category: parent category if nested (null if not found)

Return as JSON."""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ProfitAndLossSchema,
            max_output_tokens=32000
        )
    )
    return ProfitAndLossSchema.model_validate_json(response.text)

def parse_balance_sheet(csv_content: str) -> BalanceSheetSchema:
    """Parse Balance Sheet with VALIDATED list structure, then transform to dict"""
    prompt = f"""Parse this Balance Sheet into structured JSON.

CSV Content:
{csv_content}

INSTRUCTIONS:
This Balance Sheet has multiple TIME PERIODS as columns (Jan 2025, Feb 2025, etc.)

For EACH account, create ONE LineItem entry PER TIME PERIOD.

Extract ALL of the following:
- statement_type: "balance_sheet"
- company_name: from first row
- as_of_date: from "As of [date]" line
- time_periods: list of period labels ["Jan 2025", "Feb 2025", "Mar 2025", ...]
- asset_items: list of LineItem objects (one per account per period)
- liability_items: list of LineItem objects (one per account per period)
- equity_items: list of LineItem objects (one per account per period)
- total_assets: list of total values per period [5488.75, 6246.60, ...]
- total_liabilities: list of total values per period
- total_equity: list of total values per period

Each LineItem must have:
- display_name: account name (e.g., "Checking", "Savings")
- value: numeric amount (use null for empty cells)
- period: time period label (e.g., "Jan 2025", "Feb 2025")
- parent_category: parent category if nested (e.g., "Bank Accounts")

EXAMPLE:
If Checking account has values: 4875.00, 4570.45, 4321.40 for Jan, Feb, Mar
Create THREE LineItem objects:
- {{"display_name": "Checking", "value": 4875.00, "period": "Jan 2025", "parent_category": "Bank Accounts"}}
- {{"display_name": "Checking", "value": 4570.45, "period": "Feb 2025", "parent_category": "Bank Accounts"}}
- {{"display_name": "Checking", "value": 4321.40, "period": "Mar 2025", "parent_category": "Bank Accounts"}}

Return as JSON."""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BalanceSheetSchemaRaw,
            max_output_tokens=32000
        )
    )
    
    raw_bs = BalanceSheetSchemaRaw.model_validate_json(response.text)
    return balance_sheet_to_dict(raw_bs)

# ==================== QUERY PROCESSING ====================
def process_query_with_code_execution(user_query: str, pl_data: Optional[ProfitAndLossSchema], 
                                     bs_data: Optional[BalanceSheetSchema]) -> dict:
    """Process user query using Gemini's code execution capability"""
    
    data_context = {
        "has_pl": pl_data is not None,
        "has_bs": bs_data is not None
    }
    
    if pl_data:
        data_context["pl_data"] = {
            "period_start": pl_data.period_start,
            "period_end": pl_data.period_end,
            "total_income": pl_data.total_income,
            "total_expenses": pl_data.total_expenses,
            "gross_profit": pl_data.gross_profit,
            "net_income": pl_data.net_income,
            "income_items": [
                {
                    "display_name": item.display_name,
                    "value": item.value,
                    "period": item.period,
                    "parent_category": item.parent_category
                }
                for item in pl_data.income_items
            ],
            "expense_items": [
                {
                    "display_name": item.display_name,
                    "value": item.value,
                    "period": item.period,
                    "parent_category": item.parent_category
                }
                for item in pl_data.expense_items
            ],
            "cogs_items": [
                {
                    "display_name": item.display_name,
                    "value": item.value,
                    "period": item.period,
                    "parent_category": item.parent_category
                }
                for item in pl_data.cogs_items
            ]
        }
    
    if bs_data:
        data_context["bs_data"] = {
            "time_periods": bs_data.time_periods,
            "as_of_date": bs_data.as_of_date,
            "total_assets": bs_data.total_assets,
            "total_liabilities": bs_data.total_liabilities,
            "total_equity": bs_data.total_equity,
            "assets": bs_data.assets,
            "liabilities": bs_data.liabilities,
            "equity": bs_data.equity
        }
    
    prompt = f"""You are a financial data analyst. Answer the following question using the provided financial data.

USER QUESTION: {user_query}

AVAILABLE FINANCIAL DATA:
```json
{json.dumps(data_context, indent=2)}
```

INSTRUCTIONS:
1. Analyze the question and determine what financial data is needed
2. Write Python code to extract and calculate the answer
3. The Balance Sheet data uses a DICT structure: assets/liabilities/equity are dicts where:
   - Keys are account names (e.g., "Checking", "Savings")
   - Values are dicts with periods as keys (e.g., {{"Apr 2025": 1201.00}})
4. Handle None/null values appropriately
5. Format monetary values with proper currency formatting
6. Provide clear, concise explanation

EXAMPLE CODE for Balance Sheet:
```python
import json

data_json = '''{json.dumps(data_context)}'''
data = json.loads(data_json)

# Access checking balance for April 2025
if data.get('has_bs'):
    bs_data = data['bs_data']
    checking_data = bs_data['assets'].get('Checking', {{}})
    april_balance = checking_data.get('Apr 2025')
    
    if april_balance is not None:
        print(f"Checking balance in Apr 2025: ${{april_balance:,.2f}}")
```

Generate and execute code to answer the question, then provide a clear summary."""

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(code_execution=types.ToolCodeExecution)],
            max_output_tokens=32000
        )
    )
    
    result = {
        "text_parts": [],
        "code_parts": [],
        "execution_results": [],
        "full_response": ""
    }
    
    for part in response.candidates[0].content.parts:
        if part.text:
            result["text_parts"].append(part.text)
            result["full_response"] += part.text + "\n"
        
        if part.executable_code:
            code = part.executable_code.code
            result["code_parts"].append(code)
            result["full_response"] += f"\n```python\n{code}\n```\n"
        
        if part.code_execution_result:
            exec_result = part.code_execution_result.output
            result["execution_results"].append(exec_result)
            result["full_response"] += f"\n{exec_result}\n"
    
    return result

# ==================== MAIN CHATBOT CLASS ====================
class AccountantChatbot:
    def __init__(self):
        self.pl_data: Optional[ProfitAndLossSchema] = None
        self.bs_data: Optional[BalanceSheetSchema] = None
        self.conversation_history = []
    
    def upload_file(self, file_bytes):
        """Upload and parse a financial statement file"""
        csv_content = excel_to_csv_string(file_bytes)
        
        identification = identify_statement_type(csv_content)
        
        if identification.statement_type == "profit_and_loss":
            self.pl_data = parse_profit_loss(csv_content)
            return {
                "type": "profit_and_loss",
                "success": True,
                "message": f"✅ P&L uploaded successfully\n- Period: {self.pl_data.period_start} to {self.pl_data.period_end}\n- Net Income: ${self.pl_data.net_income:,.2f}" if self.pl_data.net_income else "✅ P&L uploaded successfully"
            }
        
        elif identification.statement_type == "balance_sheet":
            self.bs_data = parse_balance_sheet(csv_content)
            return {
                "type": "balance_sheet",
                "success": True,
                "message": f"✅ Balance Sheet uploaded successfully\n- Time Periods: {', '.join(self.bs_data.time_periods)}\n- Asset Accounts: {len(self.bs_data.assets)}"
            }
        
        else:
            return {
                "type": "unknown",
                "success": False,
                "message": "⚠️ Could not identify statement type"
            }
    
    def ask(self, user_query: str) -> dict:
        """Process a user query using Gemini code execution"""
        if not self.pl_data and not self.bs_data:
            return {
                "success": False,
                "message": "Please upload a financial statement first."
            }
        
        result = process_query_with_code_execution(user_query, self.pl_data, self.bs_data)
        
        return {
            "success": True,
            "response": result["full_response"],
            "code": result["code_parts"],
            "execution": result["execution_results"]
        }

# ==================== STREAMLIT UI ====================

def main():
    st.set_page_config(
        page_title="AI Accountant Chatbot",
        page_icon="💼",
        layout="wide"
    )
    
    # Initialize session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = AccountantChatbot()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'pl_uploaded' not in st.session_state:
        st.session_state.pl_uploaded = False
    if 'bs_uploaded' not in st.session_state:
        st.session_state.bs_uploaded = False
    
    # Header
    st.title("💼 AI Accountant Chatbot")
    st.markdown("Upload your financial statements and ask questions about your data!")
    
    # Sidebar for file uploads
    with st.sidebar:
        st.header("📁 Upload Financial Statements")
        
        # Balance Sheet Upload
        st.subheader("Balance Sheet")
        bs_file = st.file_uploader(
            "Upload Balance Sheet (Excel)", 
            type=['xlsx', 'xls'],
            key="bs_upload"
        )
        if bs_file and not st.session_state.bs_uploaded:
            with st.spinner("Processing Balance Sheet..."):
                result = st.session_state.chatbot.upload_file(bs_file)
                if result["success"]:
                    st.success(result["message"])
                    st.session_state.bs_uploaded = True
                else:
                    st.error(result["message"])
        
        # P&L Upload
        st.subheader("Profit & Loss")
        pl_file = st.file_uploader(
            "Upload P&L Statement (Excel)", 
            type=['xlsx', 'xls'],
            key="pl_upload"
        )
        if pl_file and not st.session_state.pl_uploaded:
            with st.spinner("Processing P&L Statement..."):
                result = st.session_state.chatbot.upload_file(pl_file)
                if result["success"]:
                    st.success(result["message"])
                    st.session_state.pl_uploaded = True
                else:
                    st.error(result["message"])
        
        # Status
        st.divider()
        st.subheader("📊 Status")
        st.write(f"✅ Balance Sheet: {'Loaded' if st.session_state.bs_uploaded else '❌ Not loaded'}")
        st.write(f"✅ P&L Statement: {'Loaded' if st.session_state.pl_uploaded else '❌ Not loaded'}")
        
        # Reset button
        if st.button("🔄 Reset All", use_container_width=True):
            st.session_state.chatbot = AccountantChatbot()
            st.session_state.messages = []
            st.session_state.pl_uploaded = False
            st.session_state.bs_uploaded = False
            st.rerun()
    
    # Main chat interface
    st.divider()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show code if available
            if message["role"] == "assistant" and "code" in message and message["code"]:
                with st.expander("🔍 View Generated Code"):
                    for i, code in enumerate(message["code"], 1):
                        st.code(code, language="python")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your financial data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.ask(prompt)
                
                if response["success"]:
                    st.markdown(response["response"])
                    
                    # Add to message history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["response"],
                        "code": response.get("code", [])
                    })
                else:
                    st.error(response["message"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response["message"]
                    })

if __name__ == "__main__":
    main()