import json
import os
import ast
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from django.conf import settings
from dotenv import load_dotenv, find_dotenv

# Force load .env
dotenv_path = find_dotenv()
print(f"DEBUG: Loading .env from: {dotenv_path}")
load_dotenv(dotenv_path, override=True)

class DisputeReasoningAgent:
    def __init__(self):
        # Load Raw Keys
        raw_openai = os.getenv("OPENAI_API_KEY")
        raw_google = os.getenv("GOOGLE_API_KEY")
        
        # Debug Raw Values (Safe)
        print(f"DEBUG: Raw OpenAI Key: {raw_openai[:5]}... (Len: {len(raw_openai)})" if raw_openai else "DEBUG: Raw OpenAI Key: None")
        print(f"DEBUG: Raw Google Key: {raw_google[:5]}... (Len: {len(raw_google)})" if raw_google else "DEBUG: Raw Google Key: None")
        
        # Validate Keys (Ignored if placeholder or too short)
        self.openai_key = raw_openai if raw_openai and "your_api" not in raw_openai and len(raw_openai) > 20 else None
        self.google_key = raw_google if raw_google and "your_key" not in raw_google and len(raw_google) > 20 else None
        
        print(f"DEBUG: Final OpenAI Key Valid: {'Yes' if self.openai_key else 'No'}")
        print(f"DEBUG: Final Google Key Valid: {'Yes' if self.google_key else 'No'}")
        
        if self.openai_key:
            self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0, openai_api_key=self.openai_key)
            print("Using OpenAI GPT-4")
        elif self.google_key:
            self.llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", temperature=0, google_api_key=self.google_key)
            print("Using Google Gemini Flash Latest")
        else:
            print("Notice: No valid API Key found. Running in Heuristic/Mock mode.")
            self.llm = None
    
    def analyze(self, dispute_text, amount, merchant_category):
        # If no LLM, use local mock
        if not self.llm:
            return self._heuristic_analyze(dispute_text, amount, merchant_category)

        system_prompt = """
        You are an expert Fintech Risk Analyst AI. Your job is to analyze transaction disputes to detect fraud, assess risk, and recommend actions.
        
        Analyze the following dispute case:
        - Description: {description}
        - Amount: ${amount}
        - Merchant Category: {category}
        
        Return a valid JSON object with the following keys:
        - classification: (String) One of [Unauthorized Transaction, Subscription Confusion, Merchant Dispute, Refund Abuse, Duplicate Charge, Unknown]
        - summary: (String) One sentence summary of the claim.
        - fraud_signals: (List[String]) List of suspicious indicators or emotional markers.
        - risk_level: (String) One of [Low, Medium, High]
        - financial_exposure: (String) Estimate of potential loss (e.g., "Full Amount", "Partial", "None")
        - recommended_action: (String) One of [Auto Approve Refund, Manual Review Required, Request Documentation, Flag Account]
        - reasoning_steps: (List[String]) Step-by-step logic used to reach the conclusion.
        
        Ensure the output is pure JSON without markdown formatting.
        """
        
        prompt = ChatPromptTemplate.from_template(system_prompt)
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "description": dispute_text,
                "amount": amount,
                "category": merchant_category
            })
            
            # Helper to extract text from simple or complex structures
            def extract_text(data):
                if isinstance(data, str):
                    return data
                elif isinstance(data, list):
                    return "".join([extract_text(item) for item in data])
                elif isinstance(data, dict):
                    return extract_text(data.get("text", ""))
                return str(data)

            # 1. Initial extraction
            content = extract_text(response.content)
            
            # Debug: Print the content before parsing
            print(f"DEBUG: Raw LLM Response: {content[:100]}...")

            # 2. Heuristic clean up (Markdown)
            def clean_markdown(text):
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                return text.strip()
            
            content = clean_markdown(content)
            
            # 3. Try standard Parse
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # 4. Parsing failed. It might be a stringified Python structure containing the text
                # e.g. "{'type': 'text', 'text': '{...}'}"
                try:
                    print("DEBUG: Standard JSON parse failed. Trying to unwrap potential dictionary frame...")
                    # Try using literal_eval to handle Python-dict syntax
                    evaluated = ast.literal_eval(content)
                    # Extract text again from this structure
                    inner_text = extract_text(evaluated)
                    inner_text = clean_markdown(inner_text)
                    print(f"DEBUG: Inner Text extracted: {inner_text[:100]}...")
                    return json.loads(inner_text)
                except Exception as e:
                    print(f"DEBUG: Deep parse failed: {e}")
                    # Last ditch: try to find the first '{' and last '}'
                    try:
                        start = content.find('{')
                        end = content.rfind('}')
                        if start != -1 and end != -1:
                            suspect_json = content[start:end+1]
                            return json.loads(suspect_json)
                    except:
                        pass
                    raise

        except Exception as e:
            print(f"Agent Error: {e}")
            if 'response' in locals():
                print(f"Raw Content type: {type(response.content)}")
            # Fallback to heuristic on API error
            print("Falling back to heuristic analysis due to API error...")
            return self._heuristic_analyze(dispute_text, amount, merchant_category)

    def _heuristic_analyze(self, text, amount, category):
        """
        Free, rule-based fallback analysis when no LLM is available.
        """
        text_lower = text.lower()
        amount = float(amount)
        
        classification = "Unknown"
        risk_level = "Low"
        recommended_action = "Manual Review"
        fraud_signals = []
        reasoning = ["Running in Heuristic Mode (No/Invalid API Key). checking keywords..."]

        is_fraud = False
        is_sub = False

        # Keyword matching
        if "fraud" in text_lower or "stolen" in text_lower or "hack" in text_lower or "unauthorized" in text_lower:
            classification = "Unauthorized Transaction"
            risk_level = "High"
            fraud_signals.append("User claims unauthorized transaction.")
            recommended_action = "Flag Account & Freeze Card"
            is_fraud = True
            reasoning.append("Detected high-risk keywords: 'fraud', 'stolen', 'unauthorized'.")
        
        elif "subscription" in text_lower or "trial" in text_lower or "cancel" in text_lower:
            classification = "Subscription Confusion"
            risk_level = "Low"
            recommended_action = "Auto Resolve" if amount < 50 else "Request Documentation"
            is_sub = True
            reasoning.append("Keywords suggest subscription cancellation issue.")

        elif "refund" in text_lower or "return" in text_lower:
            classification = "Refund Abuse" if amount > 200 else "Merchant Dispute"
            risk_level = "Medium"
            recommended_action = "Request Documentation"
            reasoning.append("Dispute involves refund request.")

        elif "twice" in text_lower or "double" in text_lower or "duplicate" in text_lower:
            classification = "Duplicate Charge"
            risk_level = "Low"
            recommended_action = "Auto Approve Refund"
            reasoning.append("User claims duplicate charge. Standard error.")

        # Logic Rules
        if amount > 500:
            risk_level = "High"
            fraud_signals.append(f"High transaction amount (${amount})")
            if not is_fraud:
                 reasoning.append(f"Transaction exceeds $500 threshold.")
                 recommended_action = "Manual Review Required"
        
        return {
            "classification": classification,
            "summary": f"User is disputing a ${amount} charge from {category}. Heuristic analysis suggests '{classification}'.",
            "fraud_signals": fraud_signals,
            "risk_level": risk_level,
            "financial_exposure": "Full Amount",
            "recommended_action": recommended_action,
            "reasoning_steps": reasoning
        }

    def _error_response(self, error_msg):
        return {
            "classification": "System Error",
            "summary": "Analysis failed due to a system error.",
            "fraud_signals": [],
            "risk_level": "High",
            "financial_exposure": "Unknown",
            "recommended_action": "Manual Review",
            "reasoning_steps": ["System error occurred:", error_msg]
        }
