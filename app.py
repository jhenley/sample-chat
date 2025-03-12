import streamlit as st
import anthropic
from datetime import datetime
import os
import time

# App title and configuration
st.set_page_config(
    page_title="Claude Chat Assistant",
    page_icon="💬",
    layout="wide",  # Use wide layout for split screen
)

# Authentication removed for public access
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True

# Custom CSS for more Material Design feel with smaller headings
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f5;
    }
    .stTextInput>div>div>input {
        border-radius: 24px;
    }
    .stButton>button {
        border-radius: 20px;
        background-color: #333333;
        color: white;
    }
    .chat-message {
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    .chat-message.user {
        background-color: #e1f5fe;
    }
    .chat-message.assistant {
        background-color: #f3e5f5;
    }
    .chat-message .avatar {
        width: 15%;
        min-width: 60px;
        padding-top: 4px;
    }
    .chat-message .content {
        width: 85%;
        padding-left: 8px;
    }
    /* Smaller headers */
    h1, h2, h3 {
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    h1 {
        font-size: 1.8rem !important;
    }
    h2 {
        font-size: 1.4rem !important;
    }
    h3 {
        font-size: 1.2rem !important;
    }
    /* Style for code blocks */
    pre {
        background-color: #f0f0f0;
        border-radius: 4px;
        padding: 12px;
        white-space: pre-wrap;
    }
    code {
        font-family: 'Courier New', Courier, monospace;
    }
    /* Style for inline code */
    p code {
        background-color: #f0f0f0;
        padding: 2px 4px;
        border-radius: 3px;
    }
    /* Style for blockquotes */
    blockquote {
        border-left: 4px solid #6200ee;
        padding-left: 16px;
        margin-left: 0;
        color: #616161;
    }
    /* Style for tables */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 10px 0;
        font-size: 0.9rem;
    }
    th, td {
        border: 1px solid #e0e0e0;
        padding: 6px 10px;
    }
    th {
        background-color: #f5f5f5;
    }
    .chat-message .content table {
        margin: 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header is now handled in the columns above

# Initialize Anthropic client
def initialize_client():
    # Try to get API key from secrets, but handle the case where secrets.toml doesn't exist
    try:
        api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    except FileNotFoundError:
        api_key = None
    
    # If no API key found in secrets or secrets file doesn't exist, prompt user
    if api_key is None:
        api_key = st.text_input("Enter your Anthropic API key:", type="password")
        if not api_key:
            st.warning("Please enter your Anthropic API key to continue.")
            st.stop()
        
    return anthropic.Anthropic(api_key=api_key)

# Initialize session state for message history and system prompt
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load system prompt from file
def load_system_prompt():
    system_prompt_path = os.path.join(os.path.dirname(__file__), "system_prompt.txt")
    try:
        with open(system_prompt_path, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "You are a helpful AI assistant that provides clear, concise answers."

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = load_system_prompt()

if "client" not in st.session_state:
    st.session_state.client = initialize_client()

# Create a three-column layout: student list, chat, and data
student_list_col, chat_col, data_col = st.columns([0.15, 0.45, 0.40])  # Students, chat, data

# Chat column content
with chat_col:
    # Model selection
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "claude-3-7-sonnet-20250219"

    # Create columns for header and model selection
    header_col, dropdown_col = st.columns([3, 1])

    with header_col:
        # App header with smaller font sizes
        st.markdown("""
            <h1 style="font-size: 1.8rem; margin-bottom: 0.2rem;">Chat with Wittly</h1>
        """, unsafe_allow_html=True)

    with dropdown_col:
        st.session_state.selected_model = st.selectbox(
            "Model",
            ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022"],
            format_func=lambda x: "Claude 3.7 Sonnet" if x == "claude-3-7-sonnet-20250219" else "Claude 3.5 Sonnet",
            label_visibility="collapsed"
        )
    
# Student list column
with student_list_col:
    st.markdown("## Students")
    
    # Add New Student button (with custom styling to ensure it remains black)
    st.markdown("""
        <style>
        /* Ensure Add New Student button stays black */
        [data-testid="stButton"] button {
            background-color: #333333 !important;
            color: white !important;
        }
        </style>
    """, unsafe_allow_html=True)
    st.button("+ Add New Student", use_container_width=True)
    
    st.markdown("---")
    
    # Display current student list with Michael selected
    if "selected_student" not in st.session_state:
        st.session_state.selected_student = "Michael Faraday"
    
    # Define student list with their status (alphabetical)
    students = [
        {"name": "Michael Faraday", "grade": "5th", "selected": True},
        {"name": "Sarah Thompson", "grade": "4th", "selected": False},
    ]
    
    # Create student list buttons with selected state styling
    st.markdown("""
        <style>
        .student-selected {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #333333;
            margin-bottom: 8px;
            font-weight: bold;
        }
        .student-unselected {
            background-color: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid transparent;
            margin-bottom: 8px;
            font-weight: normal;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Create a styled button for each student
    for student in students:
        is_selected = st.session_state.selected_student == student["name"]
        student_class = "student-selected" if is_selected else "student-unselected"
        
        st.markdown(f"""
        <div class="{student_class}">
            {student["name"]}<br>
            <small style="color: #666;">{student["grade"]} Grade</small>
        </div>
        """, unsafe_allow_html=True)
    
# Add data column with tabs
with data_col:
    # Create tabs for different data sections
    tabs = st.tabs(["Student Details", "Screener", "Progress Monitoring", "Classroom Observations"])
    
    # Student Details tab
    with tabs[0]:
        st.markdown("### Student Information")
        st.markdown("""
        **Name:** Michael Faraday  
        **Grade:** 5th Grade  
        **Age:** 10  
        **Teacher:** Jerry Henley  
        """)
        
        st.markdown("### Demographic Information")
        demo_data = {
            "Gender": "Male",
            "Special Education": "No",
            "English Language Learner": "No",
            "Economically Disadvantaged": "No"
        }
        st.table(demo_data)
        
    # Screener tab
    with tabs[1]:
        st.markdown("### Universal Screener Results")
        st.markdown("**Winter Assessment (December 2023)**")
        winter_data = {
            "Domain": ["Reading", "Math", "Grammar/Usage", "Word Analysis"],
            "Score": [320, 360, 320, 440],
            "Percentile": [10, 18, 12, 35],
            "Grade Level Equivalent": ["2nd", "4th", "2nd", "5th"]
        }
        st.dataframe(winter_data)
        
        st.markdown("**Spring Assessment (March 2024)**")
        spring_data = {
            "Domain": ["Reading", "Math", "Grammar/Usage", "Word Analysis"],
            "Score": [360, 380, 370, 490],
            "Percentile": [18, 24, 22, 45],
            "Grade Level Equivalent": ["4th", "4th", "4th", "5th"]
        }
        st.dataframe(spring_data)
        
    # Progress Monitoring tab
    with tabs[2]:
        st.markdown("### Weekly Progress Monitoring")
        progress_scores = [77, 62, 0, 85, 69, 69, 69, 85, 0, 0, 100, 0]
        progress_dates = ["Mar 21", "Mar 25", "Mar 31 (Skip)", "Apr 8", "Apr 15", 
                         "Apr 22", "May 1", "May 10", "May 12 (Skip)", 
                         "May 19 (Skip)", "May 30", "Jun 2 (Skip)"]
        
        st.line_chart(progress_scores)
        st.markdown("**Weekly Assessments:**")
        progress_data = {
            "Date": progress_dates,
            "Score": progress_scores,
        }
        st.dataframe(progress_data)
        
    # Classroom Observations tab
    with tabs[3]:
        st.markdown("### Teacher Observations")
        st.markdown("""
        - Struggles with reading comprehension but excels in word analysis
        - Strong mathematical reasoning but inconsistent performance
        - Enjoys hands-on activities and group work
        - Sometimes has difficulty maintaining focus during long reading tasks
        - Shows interest in science-related topics
        - Participates actively in class discussions
        """)
        
        st.markdown("### Behavior Notes")
        st.markdown("""
        - Generally well-behaved
        - Works well with peers
        - Occasionally frustrated when struggling with reading tasks
        - Needs occasional redirection during independent work
        """)

# Continue within chat_col to put the chat UI only in the left column
with chat_col:
    # Auto-start conversation if it's a new session
    if "conversation_started" not in st.session_state:
        st.session_state.conversation_started = True
        
        # Set up for Wittly's initial greeting
        try:
            # Add a hidden user message to trigger the conversation
            st.session_state.messages.append({
                "role": "user", 
                "content": "Please introduce yourself according to your system instructions."
            })
            
            # Set the streaming flag to true to initiate streaming on next rerun
            st.session_state.is_streaming = True
            
            # Force a rerun to start streaming the response
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred starting the conversation: {str(e)}")

    # Hide the default sidebar
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Skip showing the initial prompt message
    messages_to_display = [msg for i, msg in enumerate(st.session_state.messages) if 
                         not (i == 0 and 
                              msg["role"] == "user" and 
                              msg["content"] == "Please introduce yourself according to your system instructions.")]

    # Display message history
    for message in messages_to_display:
        with st.container():
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.markdown(f"""
                <div class="chat-message user">
                    <div class="avatar">👤 You:</div>
                    <div class="content">{content.strip()}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                # For assistant messages, use Streamlit's markdown renderer
                # to properly handle code blocks, lists, etc.
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(content)

# Add a state for tracking if we're currently streaming a response
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

# Function to handle the conversation 
def handle_send():
    user_input = st.session_state.current_input
    if user_input:  # Only process if there's actual input
        # Set streaming flag
        st.session_state.is_streaming = True
        # Clear input
        st.session_state.current_input = ""
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_input})
        # Rerun to show the user message immediately
        st.rerun()

# Function to handle streaming response
def stream_response():
    # We need to make sure to display this in the chat column
    with chat_col:
        # Create a chat message with the robot avatar for streaming
        with st.chat_message("assistant", avatar="🤖"):
            streaming_placeholder = st.empty()
            full_response = ""
        
        try:
            # Make a streaming request
            with st.session_state.client.messages.stream(
                model=st.session_state.selected_model,
                max_tokens=4000,
                system=st.session_state.system_prompt,
                messages=[
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ]
            ) as stream:
                # Display the response as it comes in
                for chunk in stream:
                    if chunk.type == "content_block_delta" and chunk.delta.text:
                        full_response += chunk.delta.text
                        streaming_placeholder.markdown(full_response)
            
            # Add the full response to history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response
            })
        except anthropic.RateLimitError:
            st.error("Rate limit exceeded. Please wait a minute before trying again.")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "I'm sorry, the API rate limit has been exceeded. Please wait a minute before sending another message."
            })
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"I'm sorry, an error occurred: {str(e)}"
            })
    
    # Reset streaming flag
    st.session_state.is_streaming = False
    st.rerun()

# No "New Conversation" button at the top anymore

# Process streaming if needed
if st.session_state.is_streaming:
    stream_response()

# Continue in the chat column for the input area
with chat_col:
    # Initialize the input state
    if "current_input" not in st.session_state:
        st.session_state.current_input = ""
    
    # Create a fixed-position container at the bottom but only for the chat column
    st.markdown("""
        <style>
        .fixed-bottom {
            position: fixed;
            bottom: 0;
            left: 15%;  /* Adjust for student list column */
            width: 45%;  /* Match the chat column width */
            background-color: #f5f5f5;
            padding: 0;
            z-index: 999;
            display: flex;
            border-top: 1px solid #ddd;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Add spacing to ensure content isn't hidden behind the fixed input box
    if len(st.session_state.messages) > 0:
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    # Create a container for the input area
    input_container = st.container()

# Custom CSS to style the input area - putting inside the chat column
with chat_col:
    st.markdown("""
        <style>
        .input-container {
            display: flex;
            align-items: flex-end;
            margin-bottom: 20px;
        }
        .input-box {
            flex-grow: 1;
            width: 100%;
        }
        /* Remove default label space */
        .input-box label {
            display: none !important;
        }
        /* Style the text area */
        .stTextArea textarea {
            resize: vertical;
            min-height: 60px;
            border-radius: 10px;
        }
        /* Style the form submit button - black and white theme */
        .stForm [data-testid="stFormSubmitButton"] button {
            border-radius: 4px;
            background-color: #333333 !important;
            color: white !important;
            border: none;
            transition: background-color 0.3s ease;
        }
        
        /* Hover state for the button */
        .stForm [data-testid="stFormSubmitButton"] button:hover {
            background-color: #000000 !important;
        }
        
        /* Style the tabs in the data column */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            border-radius: 5px 5px 0 0;
            padding: 10px 20px;
            background-color: #f5f5f5;
        }
        .stTabs [aria-selected="true"] {
            background-color: white;
            border-top: 2px solid #333333;
        }
        
        /* Style student list */
        [data-testid="stVerticalBlock"] > div:nth-child(1) [data-testid="stMarkdownContainer"] h2 {
            margin-top: 0;
            padding-top: 0;
            font-size: 1.3rem;
        }
        </style>
    """, unsafe_allow_html=True)

# Function to handle enter key press (no longer used)
def handle_key_press():
    if not st.session_state.is_streaming and st.session_state.current_input:
        handle_send()

with chat_col:
    with input_container:
        # Create a two-column layout with custom CSS
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        # Input field column
        st.markdown('<div class="input-box">', unsafe_allow_html=True)
        
        # Create a form to enable proper Enter key handling
        with st.form(key="message_form", clear_on_submit=True):
            # Use text_area instead of text_input for multi-line support
            user_input = st.text_area(
                "Your message:", 
                key="user_input_field",
                placeholder="Ask Wittly something...",
                value=st.session_state.current_input,
                height=70)  # Smaller fixed height for the text area
                
            # Show the form's submit button
            submit_button = st.form_submit_button("Send")
            
            # Handle form submission
            if submit_button and not st.session_state.is_streaming:
                st.session_state.current_input = user_input
                if user_input:
                    handle_send()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # End the input-container div
        st.markdown('</div>', unsafe_allow_html=True)

# Display minimal footer information in the chat column
with chat_col:
    st.caption(f"Session started: {datetime.now().strftime('%Y-%m-%d %H:%M')} | API key is used only for this session")