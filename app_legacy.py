"""
AI Agent Interface - Premium Streamlit Application
Inspired by Endee.io's modern, minimalist SaaS design
"""

import streamlit as st
from datetime import datetime


# PAGE CONFIGURATION


st.set_page_config(
    page_title="AI Agent Interface",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# CUSTOM CSS INJECTION


custom_css = """
<style>
    /* Hide default Streamlit header and footer for clean aesthetic */
    #MainMenu {
        visibility: hidden;
    }
    
    footer {
        visibility: hidden;
    }
    
    header {
        visibility: hidden;
    }
    
    /* Adjust main content padding for better spacing */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Feature Card Styling */
    .feature-card {
        border: 1px solid #2D3139;
        border-radius: 8px;
        background-color: #13161C;
        padding: 1.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    .feature-card:hover {
        border-color: #2563EB;
        background-color: #191D26;
        box-shadow: 0 4px 16px rgba(37, 99, 235, 0.15);
        transform: translateY(-2px);
    }
    
    .feature-card-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #2563EB;
        margin-bottom: 0.5rem;
    }
    
    .feature-card-desc {
        font-size: 0.95rem;
        color: #9CA3AF;
        line-height: 1.5;
    }
    
    /* Hero Title Styling */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        color: #F3F4F6;
        text-align: center;
        margin-bottom: 1rem;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.25rem;
        color: #9CA3AF;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Custom Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4);
        transform: translateY(-1px);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }
    
    /* Chat Container Styling */
    .chat-container {
        background-color: #0B0D10;
        border: 1px solid #2D3139;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Metric Cards Enhancement */
    .metric-container {
        background-color: #13161C;
        border: 1px solid #2D3139;
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
    }
    
    /* Text Color Enhancements */
    .metric-value {
        color: #2563EB;
        font-weight: 700;
        font-size: 1.75rem;
    }
    
    .metric-label {
        color: #9CA3AF;
        font-size: 0.9rem;
    }
    
    /* Divider Style */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #2D3139, transparent);
        margin: 2rem 0;
    }
    
    /* Chat Input Styling */
    .stChatInput {
        background-color: #181B21;
        border: 1px solid #2D3139;
        border-radius: 8px;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        background-color: transparent;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# INITIALIZE SESSION STATE


if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "🔵 System initialized. Vector database connected. How can I assist you today?",
        }
    ]

if "initialized" not in st.session_state:
    st.session_state.initialized = False


# SECTION 1: HERO SECTION


def render_hero_section():
    """Render the premium hero section with title and CTA"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(
            '<div class="hero-title">AI Agent Interface</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="hero-subtitle">Powered by High-Performance Vector Retrieval</div>',
            unsafe_allow_html=True,
        )
        
        # Center-align the button using columns
        button_col1, button_col2, button_col3 = st.columns([1, 1, 1])
        with button_col2:
            if st.button("🚀 Initialize Agent", key="init_agent", use_container_width=True):
                st.session_state.initialized = True
                st.success("Agent initialized and ready for queries!")
                st.session_state.messages = [
                    {
                        "role": "assistant",
                        "content": "✅ System ready. I'm prepared to assist with semantic search, information retrieval, and multi-step reasoning. What would you like to explore?",
                    }
                ]
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)



# SECTION 2: PERFORMANCE METRICS


def render_performance_metrics():
    """Display performance metrics in a 4-column grid"""
    st.subheader("⚡ Performance Benchmarks", divider="blue")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    metrics = [
        {"label": "Queries/sec", "value": "10,000+", "delta": "+25%"},
        {"label": "Latency", "value": "<5ms", "delta": "-30%"},
        {"label": "Recall", "value": "99%+", "delta": "+15%"},
        {"label": "Memory", "value": "10x Less", "delta": "-40%"},
    ]
    
    metric_columns = [metric_col1, metric_col2, metric_col3, metric_col4]
    
    for col, metric in zip(metric_columns, metrics):
        with col:
            st.metric(
                label=metric["label"],
                value=metric["value"],
                delta=metric["delta"],
                label_visibility="visible",
            )
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)



# SECTION 3: AI AGENT CHAT INTERFACE


def render_chat_interface():
    """Render the multi-turn chat interface"""
    st.subheader("💬 Agent Conversation", divider="blue")
    
    # Chat container
    with st.container(border=True):
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if st.session_state.initialized:
            user_input = st.chat_input(
                "Ask a question...",
                key="chat_input",
            )
            
            if user_input:
                # Add user message to session state
                st.session_state.messages.append(
                    {
                        "role": "user",
                        "content": user_input,
                    }
                )
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(user_input)
                
                # Simulate agent response (replace with real agent logic)
                with st.chat_message("assistant"):
                    with st.spinner("Processing..."):
                        # Mock response - replace with your actual agent
                        response = generate_agent_response(user_input)
                        st.markdown(response)
                        
                        # Add to session state
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": response,
                            }
                        )
        else:
            st.info("🔒 Initialize the agent to begin conversation.", icon="ℹ️")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)



# SECTION 4: FEATURE CARDS / CAPABILITIES GRID


def render_feature_cards():
    """Display capability cards in a 3-column grid"""
    st.subheader("🎯 Capabilities", divider="blue")
    
    card_col1, card_col2, card_col3 = st.columns(3, gap="medium")
    
    features = [
        {
            "title": "Semantic Search",
            "description": "Meaning-based query understanding that goes beyond keyword matching. Retrieve relevant information using contextual understanding.",
        },
        {
            "title": "Multi-Step Reasoning",
            "description": "Tool orchestration and complex reasoning chains. Break down complex problems into manageable steps for superior solutions.",
        },
        {
            "title": "Context Retrieval",
            "description": "Infinite memory scaling with efficient vector storage. Maintain conversation context and retrieve historical information seamlessly.",
        },
    ]
    
    feature_columns = [card_col1, card_col2, card_col3]
    
    for col, feature in zip(feature_columns, features):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div>
                        <div class="feature-card-title">{feature['title']}</div>
                        <div class="feature-card-desc">{feature['description']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )



# MOCK AGENT RESPONSE GENERATOR


def generate_agent_response(user_input: str) -> str:
    """
    Generate a mock agent response.
    
    Replace this with your actual agent logic (LLM calls, vector DB queries, etc.)
    """
    response_templates = [
        f"I've analyzed your query: '{user_input}'. Based on the vector database, I found 5 highly relevant documents with a semantic similarity score of 0.94.",
        f"Processing your request: '{user_input}'. Using multi-step reasoning, I identified three key information chunks that answer your question.",
        f"Your question '{user_input}' was excellent. The context retrieval system pulled up 8 relevant passages. Here's what I found...",
        f"I understand you're asking about '{user_input}'. Let me search the knowledge base for the most relevant information.",
    ]
    
    import random
    base_response = random.choice(response_templates)
    
    return f"{base_response}\n\n📊 **Confidence Score:** 92%\n⏱️ **Query Time:** 2.3ms"



# MAIN APPLICATION FLOW


def main():
    """Main application entry point"""
    # Render sections in order
    render_hero_section()
    render_performance_metrics()
    render_chat_interface()
    render_feature_cards()
    
    # Footer
    st.markdown(
        """
        ---
        <div style='text-align: center; color: #6B7280; font-size: 0.85rem;'>
            <p>✨ Built with Streamlit | Powered by Advanced Vector Retrieval</p>
            <p style='margin: 0.5rem 0;'>© 2026 AI Agent Interface. Premium Vector Database Technology.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
