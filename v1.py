import pandasai
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pandasai import Agent
from pandasai.connectors import PandasConnector
from langchain_groq.chat_models import ChatGroq
import os
import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import pyperclip
import zipfile

pandasai.clear_cache()

# Page configuration
st.set_page_config(
    page_title="Data Analysis Assistant | CSV Analysis Made Easy",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.linkedin.com/in/neelesh-vs-9676b8214/',
        'Report a bug': 'https://www.linkedin.com/in/neelesh-vs-9676b8214/',
        'About': """
        # Data Analysis Assistant
        This powerful tool helps you analyze CSV data through natural language conversations.
        
        Created by V S Neelesh
        """
    }
)


# Add meta tags and SEO optimization
st.markdown("""
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Free AI-powered CSV data analysis tool. Upload your CSV and get instant insights through natural conversation. Created by V S Neelesh. An application which can help you chat with csv.">
        <meta name="keywords" content="data analysis, CSV analysis, AI assistant, data visualization, pandas, streamlit, python, data science, chatwithcsv, csv, chatbot, data extractor">
        <meta name="author" content="V S Neelesh">
        
    </head>
""", unsafe_allow_html=True)

# Add cookie consent
st.markdown("""
    <script>
        function showCookieConsent() {
            const consent = document.createElement('div');
            consent.style.cssText = `
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background-color: #f8f9fa;
                padding: 1rem;
                text-align: center;
                border-top: 1px solid #dee2e6;
                z-index: 1000;
            `;
            consent.innerHTML = `
                This website uses cookies to enhance your experience. 
                <button onclick="acceptCookies()" style="
                    background-color: #0066cc;
                    color: white;
                    border: none;
                    padding: 0.5rem 1rem;
                    border-radius: 5px;
                    margin-left: 1rem;
                    cursor: pointer;
                ">Accept</button>
            `;
            document.body.appendChild(consent);
        }
        
        function acceptCookies() {
            localStorage.setItem('cookieConsent', 'true');
            document.querySelector('div[role="alert"]').remove();
        }
        
        if (!localStorage.getItem('cookieConsent')) {
            showCookieConsent();
        }
    </script>
""", unsafe_allow_html=True)

# Add loading animation
with open("style.css", "w") as f:
    f.write("""
    /* Add this to your existing CSS */
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background-color: rgba(255, 255, 255, 0.9);
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 9999;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid #0066cc;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    """)



# Custom CSS for better UI

# /* ================ COMPLETE UPDATED CSS ================ */
st.markdown("""
    <style>
    /* General Styles */
    .stTitle {
        font-size: 3rem !important;
        padding-bottom: 2rem;
    }

    .stTabs button {
        font-size: 1.1rem;
    }

    /* Upload Section */
    .upload-section {
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #cccccc;
        text-align: center;
        background-color: #fafafa;
        transition: border-color 0.3s ease;
    }

    .upload-section:hover {
        border-color: #0066cc;
    }

    /* Header Section */
    .header-section {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }

    /* Disclaimer */
    .disclaimer {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        border-radius: 8px;
        padding: 1.25rem;
        margin: 1.25rem 0;
        font-size: 0.95rem;
        color: #856404;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    /* Sample Questions */
    .sample-question {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.75rem 0;
        border-left: 3px solid #0066cc;
        transition: transform 0.2s ease;
    }

    .sample-question:hover {
        transform: translateX(5px);
    }

    /* Chat Container and Messages */
    .chat-container {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.25rem 0;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }

    .message-wrapper {
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
        padding-bottom: 1.5rem;
    }

    .message-wrapper:last-child {
        border-bottom: none;
        margin-bottom: 0;
        padding-bottom: 0;
    }

    .user-message {
        background-color: #f0f2f6;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #e6e9ef;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .assistant-message {
        background-color: #ffffff;
        padding: 1.25rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    }

    .user-label {
        font-weight: 600;
        color: #0066cc;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }

    .assistant-label {
        font-weight: 600;
        color: #43a047;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }

    .message-content {
        margin-top: 0.5rem;
        line-height: 1.5;
    }

    .message-content img {
        max-width: 100%;
        border-radius: 8px;
        margin: 1rem 0;
    }

    /* Chat Input Area */
    .stTextArea textarea {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 1rem;
        resize: vertical;
        min-height: 100px;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        transition: border-color 0.2s ease;
    }

    .stTextArea textarea:focus {
        border-color: #0066cc;
        box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.1);
    }

    /* Chat Controls */
    .chat-controls {
        display: flex;
        gap: 1rem;
        margin-top: 1rem;
    }

    /* Error Message */
    .error-message {
        background-color: #ffebee;
        border: 1px solid #ffcdd2;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
        color: #c62828;
    }

    /* Loading Spinner */
    .loading-spinner {
        text-align: center;
        padding: 1rem;
        color: #666666;
    }

    /* Download Button */
    .download-button {
        display: inline-block;
        padding: 0.5rem 1rem;
        background-color: #0066cc;
        color: white !important;
        text-decoration: none;
        border-radius: 6px;
        transition: all 0.2s ease;
    }

    .download-button:hover {
        background-color: #0055aa;
        text-decoration: none;
        transform: translateY(-1px);
    }

    /* Scroll to Top Button */
    #ScrollToTop {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 99;
        border: none;
        outline: none;
        background-color: #0066cc;
        color: white;
        cursor: pointer;
        padding: 15px;
        border-radius: 50%;
        font-size: 18px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }

    #ScrollToTop:hover {
        background-color: #005299;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Data Preview and Visualization */
    .dataframe {
        font-size: 0.9rem !important;
    }

    .plot-container {
        margin: 1rem 0;
        padding: 1rem;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }

    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .chat-container {
            padding: 1rem;
        }
        
        .user-message, .assistant-message {
            padding: 1rem;
        }
        
        .stTitle {
            font-size: 2rem !important;
        }
        
        .disclaimer {
            padding: 1rem;
        }

        .message-wrapper {
            margin-bottom: 1rem;
            padding-bottom: 1rem;
        }
            
        
    }
    </style>
""", unsafe_allow_html=True)

# Add JavaScript for clipboard functionality and scroll behavior
st.markdown("""
    <script>
        async function copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                // Show success message
                const toast = document.createElement('div');
                toast.textContent = 'Copied to clipboard!';
                toast.style.position = 'fixed';
                toast.style.bottom = '20px';
                toast.style.left = '50%';
                toast.style.transform = 'translateX(-50%)';
                toast.style.backgroundColor = '#4CAF50';
                toast.style.color = 'white';
                toast.style.padding = '10px 20px';
                toast.style.borderRadius = '5px';
                toast.style.zIndex = '1000';
                document.body.appendChild(toast);
                setTimeout(() => toast.remove(), 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        }

        function scrollToTopOfChat() {
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            }
        }
    </script>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Initialize the LLM model
model = ChatGroq(
    model="llama-3.2-90b-vision-preview",
    temperature=0.1,
    api_key=os.environ["GROQ_API_KEY"]
)

def extract_json_from_response(response):
    """Extract JSON from LLM response, handling different response formats."""
    response_text = response.content if hasattr(response, 'content') else str(response)
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > 0:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except:
            return None
    return None

def generate_sample_questions(data):
    """Generate sample questions and answers based on the dataset."""
    data_info = f"Column names: {', '.join(data.columns)}\n"
    data_info += "Sample data (first 5 rows):\n"
    data_info += data.head().to_string()
    
    prompt = f"""As a data analyst, generate 15 insightful questions and their answers for this dataset.
    
Data Information:
{data_info}

Instructions:
1. Generate 15 diverse questions that showcase different types of analysis
2. Include questions about trends, patterns, statistics, and relationships
3. Provide clear, concise answers
4. Format as JSON with "questions" array containing objects with "question" and "answer" fields

Example format:
{{
    "questions": [
        {{"question": "What is the average value of X?", "answer": "The average value is Y"}},
        {{"question": "How many unique entries are in column Z?", "answer": "There are N unique entries"}}
    ]
}}

Provide only the JSON response."""

    try:
        response = model.invoke(prompt)
        questions = extract_json_from_response(response)
        
        if questions is None or 'questions' not in questions:
            return generate_default_questions()
            
        return questions['questions']
    
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        return generate_default_questions()

def generate_default_questions():
    """Generate default questions if the LLM fails."""
    return [
        {"question": "What is the total number of rows in the dataset?", "answer": "You can check this in the Data Overview section."},
        {"question": "What are the main columns in this dataset?", "answer": "Check the Column Descriptions tab for details."},
        {"question": "Can you show me basic statistics for numerical columns?", "answer": "I can calculate mean, median, and standard deviation for numerical columns."},
        {"question": "What are the unique values in categorical columns?", "answer": "I can list unique values and their frequencies."},
        {"question": "Are there any missing values in the dataset?", "answer": "I can check for null values in each column."},
        {"question": "Can you create a summary visualization?", "answer": "I can create various plots based on your data type."},
        {"question": "What are the correlations between numerical columns?", "answer": "I can calculate and visualize correlations."},
        {"question": "Can you show the distribution of values?", "answer": "I can create histograms or box plots."},
        {"question": "What are the minimum and maximum values?", "answer": "I can find the range for numerical columns."},
        {"question": "Can you identify any outliers?", "answer": "I can use statistical methods to detect outliers."}
    ]

def generate_column_descriptions(data):
    """Generate descriptions for columns using LLM."""
    data_info = f"Column names: {', '.join(data.columns)}\n\n"
    data_info += "Sample data (first 5 rows):\n"
    data_info += data.head().to_string()
    
    prompt = f"""As a data analyst, generate clear descriptions for each column in this dataset.
    
Data Information:
{data_info}

Instructions:
1. For each column, write a clear 1-2 sentence description explaining what the data represents
2. Format your response as a JSON object where keys are column names and values are descriptions
3. Focus on the practical meaning and use of each column
4. Be concise but informative

Example format:
{{
    "column_name": "This column represents... It is used for...",
    "another_column": "Contains information about... Used to track..."
}}

Provide only the JSON response without any additional text."""

    try:
        response = model.invoke(prompt)
        descriptions = extract_json_from_response(response)
        
        if descriptions is None:
            st.error("Failed to generate proper descriptions. Using default ones.")
            descriptions = {col: f"Description for {col}" for col in data.columns}
        
        for col in data.columns:
            if col not in descriptions:
                descriptions[col] = f"Description for {col}"
                
        return descriptions
    
    except Exception as e:
        st.error(f"Error in description generation: {str(e)}")
        return {col: f"Description for {col}" for col in data.columns}

class CustomAgent(Agent):
    def handle_plot(self, fig):
        """Custom handler for matplotlib figures to display in Streamlit"""
        buf = BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        return buf.getvalue()

    def chat(self, prompt: str) -> str:
        """Override chat method to handle both text and image responses"""
        response = super().chat(prompt)
        
        if plt.get_fignums():
            fig = plt.gcf()
            img_bytes = self.handle_plot(fig)
            plt.close()
            return {
                'type': 'image',
                'content': img_bytes,
                'text': response
            }
        return {
            'type': 'text',
            'content': response
        }

def export_chat_history(chat_history):
    try:
        # Create a ZIP file in memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add text chat history
            chat_export = "Data Analysis Chat History\n" + "=" * 50 + "\n\n"
            image_counter = 1
            
            for chat in chat_history:
                if "timestamp" in chat:
                    chat_export += f"Time: {chat['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}\n"
                
                chat_export += f"Question: {chat['query']}\n"
                chat_export += "Answer: "
                
                if isinstance(chat['response'], dict):
                    if chat['response']['type'] == 'text':
                        chat_export += f"{chat['response']['content']}\n"
                    elif chat['response']['type'] == 'image':
                        # Save visualization to ZIP
                        image_filename = f"visualization_{image_counter}.png"
                        zip_file.writestr(image_filename, chat['response']['content'])
                        chat_export += f"[See visualization: {image_filename}]\n"
                        if chat['response'].get('text'):
                            chat_export += f"Description: {chat['response']['text']}\n"
                        image_counter += 1
                else:
                    chat_export += f"{chat['response']}\n"
                
                chat_export += "-" * 50 + "\n\n"
            
            # Add the text file to ZIP
            zip_file.writestr("chat_history.txt", chat_export)
        
        # Create download button for ZIP
        zip_buffer.seek(0)
        b64 = base64.b64encode(zip_buffer.getvalue()).decode()
        filename = f"chat_history_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.zip"
        href = f'<a href="data:application/zip;base64,{b64}" download="{filename}" class="download-button">Download Chat History (with visualizations)</a>'
        st.markdown(href, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error exporting chat history: {str(e)}")

# Sidebar
with st.sidebar:
    st.image("C:/Users/vsnee/Documents/coding/GenAI/Chatwithcsv_openai/chatwithcsv_v1/csv_logo.jpeg", caption="Data Analysis Assistant",width=250)

    st.markdown("### About")
    st.markdown("""
        This AI-powered assistant helps you analyze CSV data through natural language conversations.
        
        **Features:**
        - Upload and analyze CSV files
        - Auto-generate column descriptions
        - Interactive data visualization
        - Natural language queries
    """)
    
    if "agent" in st.session_state:
        st.success("✅ Agent is active")
    
    if st.button("❌ Clear All", type="secondary"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.title("📊 Data Analysis Assistant")
st.markdown("Upload your CSV file and start exploring your data through natural conversation")

# Disclaimer
st.markdown("""
    <div class="disclaimer">
        <strong>ℹ️ Please Note:</strong><br>
        • The AI assistant may occasionally produce inaccurate results or interpretations<br>
        • Column descriptions are automatically generated and may need manual refinement<br>
        • The agent's behavior can be customized through the configuration panel<br>
        • Always verify critical insights and decisions with domain experts
    </div>
""", unsafe_allow_html=True)

# st.markdown('</div>', unsafe_allow_html=True)

# File upload
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["csv"])
if not uploaded_file:
    st.markdown("### 📎 Drop your CSV file here or click to upload")
st.markdown('</div>', unsafe_allow_html=True)

# Initialize session state
if "field_descriptions" not in st.session_state:
    st.session_state.field_descriptions = {}
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "sample_questions" not in st.session_state:
    st.session_state.sample_questions = []

# Handle file upload and processing
if uploaded_file is not None:
    if "current_file" not in st.session_state or st.session_state.current_file != uploaded_file.name:
        st.session_state.file_processed = False
        st.session_state.current_file = uploaded_file.name
        st.session_state.field_descriptions = {}
        st.session_state.sample_questions = []

    data = pd.read_csv(uploaded_file)
    
    if not st.session_state.file_processed:
        st.success("✅ CSV File Loaded Successfully!")
        with st.spinner("🔄 Analyzing your data..."):
            st.session_state.field_descriptions = generate_column_descriptions(data)
            st.session_state.sample_questions = generate_sample_questions(data)
            st.session_state.file_processed = True

    # Data overview section
    st.markdown("### 📋 Data Overview")
    overview_tab, desc_tab, preview_tab, questions_tab = st.tabs([
        "Summary", "Column Descriptions", "Data Preview", "Sample Questions"
    ])
    
    with overview_tab:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{len(data):,}")
        with col2:
            st.metric("Total Columns", f"{len(data.columns):,}")
        with col3:
            st.metric("Memory Usage", f"{data.memory_usage().sum() / 1024**2:.2f} MB")
    
    with desc_tab:
        for column in data.columns:
            with st.expander(f"📝 {column}"):
                current_description = st.session_state.field_descriptions.get(column, f"Description for {column}")
                new_description = st.text_area(
                    "Edit description:",
                    value=current_description,
                    key=f"desc_{column}",
                    height=100
                )
                st.session_state.field_descriptions[column] = new_description
    
    with preview_tab:
        st.dataframe(
            data.head(),
            use_container_width=True,
            hide_index=False
        )
    
    # with questions_tab:
    #     st.markdown("### 🤔 Sample Questions You Can Ask")
    #     st.markdown("""
    #         Below are some example questions you can ask about your dataset. 
    #         Click on any question to copy it to your clipboard!
    #     """)
        
    #     for i, qa in enumerate(st.session_state.sample_questions, 1):
    #         with st.expander(f"❓ Question {i}: {qa['question']}"):
    #             st.markdown("**Answer:**")
    #             st.markdown(qa['answer'])
    #             if st.button(f"📋 Copy Question {i}", key=f"copy_q_{i}"):
    #                 st.write(qa['question'])

    with questions_tab:
        st.markdown("### 🤔 Sample Questions You Can Ask")
        st.markdown("""
            Below are some example questions you can ask about your dataset. 
            Click any 'Copy' button to copy the question to your clipboard!
        """)
        
        for i, qa in enumerate(st.session_state.sample_questions, 1):
            with st.expander(f"❓ Question {i}: {qa['question']}"):
                st.markdown("**Answer:**")
                st.markdown(qa['answer'])
                if st.button(f"📋 Copy Question", key=f"copy_q_{i}"):
                    try:
                        pyperclip.copy(qa['question'])
                        st.success("Question copied to clipboard!")
                    except Exception as e:
                        st.error(f"Failed to copy: {str(e)}")
                        # Fallback JavaScript method
                        st.markdown(
                            f"""
                            <script>
                                copyToClipboard("{qa['question']}");
                            </script>
                            """,
                            unsafe_allow_html=True
                        )

    # Agent Configuration
    with st.expander("⚙️ Agent Configuration"):
        agent_description = st.text_area(
            "Customize the agent's behavior:",
            value="You are an advanced data analysis agent specializing in extracting and analyzing data from CSV files. Your main goal is to derive meaningful insights from the provided dataset. Use the column descriptions provided to better understand the context of each field."
        )

    if st.button("🤖 Initialize Agent", type="primary"):
        with st.spinner("Initializing AI Agent..."):
            connector = PandasConnector(
                {"original_df": data}, 
                field_descriptions=st.session_state.field_descriptions
            )

            st.session_state.agent = CustomAgent(
                dfs=connector,
                config={"llm": model},
                description=agent_description
            )

            st.success("✨ Agent initialized successfully!")


# Chat Interface
if "agent" in st.session_state:
    st.header("💬 Chat with Your Data")
    
    # Initialize chat history if not present
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Create a single container for all chat messages
    with st.container():
        for chat in st.session_state.chat_history:
            # Message wrapper div
            st.markdown('<div class="message-wrapper">', unsafe_allow_html=True)
            
            # User message
            st.markdown(
                f"""
                <div class="user-message">
                    <div class="user-label">🧑‍💼 You:</div>
                    <div class="message-content">{chat["query"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Assistant message
            # st.markdown(
            #     '<div class="assistant-message">',
            #     unsafe_allow_html=True
            # )
            st.markdown(
                '<div class="assistant-label">🤖 Assistant:</div>',
                unsafe_allow_html=True
            )
            
            # Handle different types of responses
            if isinstance(chat["response"], dict):
                if chat["response"]["type"] == "image":
                    # Display text response if present
                    if chat["response"].get("text"):
                        st.markdown(
                            f'<div class="message-content">{chat["response"]["text"]}</div>',
                            unsafe_allow_html=True
                        )
                    
                    # Display visualization within the message
                    try:
                        st.image(
                            chat["response"]["content"],
                            caption="Generated Visualization",
                            use_column_width=True
                        )
                    except Exception as e:
                        st.error(f"Error displaying visualization: {str(e)}")
                else:
                    # Text-only response
                    st.markdown(
                        f'<div class="message-content">{chat["response"]["content"]}</div>',
                        unsafe_allow_html=True
                    )
            else:
                # Plain text response
                st.markdown(
                    f'<div class="message-content">{chat["response"]}</div>',
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close assistant message
            st.markdown('</div>', unsafe_allow_html=True)  # Close message wrapper
        

    # Chat input form
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Ask a question about your data:",
            key="user_input",
            height=100,
            placeholder="e.g., 'What are the top 5 values in column X?' or 'Create a bar chart showing...'"
        )
        
        submit_button = st.form_submit_button(
            "Send 📤",
            type="primary"
        )

        if submit_button and user_input.strip():
            with st.spinner("🤔 Analyzing..."):
                try:
                    response = st.session_state.agent.chat(user_input)
                    st.session_state.chat_history.append({
                        "query": user_input,
                        "response": response,
                        "timestamp": pd.Timestamp.now()
                    })
                    st.rerun()
                except Exception as e:
                    st.error("⚠️ Error processing request")
                    st.markdown(
                        f"""
                        <div class="error-message">
                            <p>Details: {str(e)}</p>
                            <p>Try rephrasing your question or check if it's related to the available data columns.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
           

    # Export chat history
    if st.session_state.chat_history:
        col1, col2 = st.columns([4, 2])

        with col1:
            if st.button("📥 Export Chat History", type="secondary"):
                export_chat_history(st.session_state.chat_history)

        with col2:
            if st.button("🗑️ Clear Chat", type="secondary"):
                if st.session_state.chat_history:
                    st.session_state.chat_history = []
                    st.rerun()

    # Add scroll to top button if there are enough messages
        # if len(st.session_state.chat_history) > 1:
        #     add_scroll_button()
   
# Add footer
# Add footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666666; padding: 1rem;'>
        <p style='margin-bottom: 0.5rem;'>Made with ❤️ by V S Neelesh</p>
        <a href="https://www.linkedin.com/in/neelesh-vs-9676b8214/" 
           target="_blank" 
           style="
               display: inline-block;
               padding: 0.5rem 1rem;
               background-color: #0077b5;
               color: white;
               text-decoration: none;
               border-radius: 5px;
               font-size: 0.9rem;
               margin: 0.5rem 0;
               transition: background-color 0.3s ease;
           "
           onmouseover="this.style.backgroundColor='#005885'"
           onmouseout="this.style.backgroundColor='#0077b5'"
        >
            Connect on LinkedIn
        </a>
        <br>
        <small>Version 1.0.0</small>
    </div>
""", unsafe_allow_html=True)
if __name__ == "__main__":
    # Add any initialization code here if needed
    pass


st.markdown("""
    <!-- Schema.org markup for Google -->
    <script type="application/ld+json">
    {
        "@context": "http://schema.org",
        "@type": "SoftwareApplication",
        "name": "Data Analysis Assistant",
        "description": "AI-powered CSV data analysis tool for instant insights through natural conversation",
        "applicationCategory": "Data Analysis Tool",
        "operatingSystem": "Web Browser",
        "author": {
            "@type": "Person",
            "name": "V S Neelesh",
            "url": "https://www.linkedin.com/in/neelesh-vs-9676b8214/"
        },
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD"
        }
    }
    </script>
""", unsafe_allow_html=True)