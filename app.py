import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import io

# Configure app
st.set_page_config(
    page_title="Optimus Alpha OCR Pro",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for futuristic design
st.markdown("""
<style>
    /* Main colors */
    :root {
        --primary: #6366f1;
        --secondary: #10b981;
        --dark: #1e293b;
        --light: #f8fafc;
    }
    
    /* Main container */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: var(--light);
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--light) !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(195deg, #0f172a 0%, #1e40af 100%) !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: var(--primary) !important;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 500;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--primary) !important;
        border-radius: 12px !important;
        padding: 20px !important;
    }
    
    /* Markdown output */
    .markdown-text {
        background: rgba(30, 41, 59, 0.7) !important;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid var(--secondary);
        animation: fadeIn 0.5s ease-in-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Streamlit text input */
    .stTextInput>div>div>input {
        background: rgba(15, 23, 42, 0.7) !important;
        color: white !important;
        border: 1px solid #334155 !important;
    }
    
    /* OCR specific styles */
    .ocr-output {
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        background: #0f172a;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #334155;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.title("🔍 Optimus Alpha OCR Pro")
st.markdown("""
**Extract text from images with high accuracy**  
Upload any image containing text and get perfectly formatted text output.
""")

# Initialize OpenAI client
@st.cache_resource
def get_client(api_key):
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

# Sidebar with info and API key input
with st.sidebar:
    st.image("blob.png", width=200)
    st.markdown("""
    **Optimus Alpha OCR Pro**  
    *Powered by OpenRouter*
    """)
    
    # API key input
    api_key = st.text_input(
        "Enter your OpenRouter API Key:",
        type="password",
        help="Get your API key from https://openrouter.ai/keys"
    )
    
    st.markdown("---")
    st.markdown("Extract text from:")
    st.markdown("""
    - Documents
    - Screenshots
    - Handwriting (printed only)
    - Receipts
    - Business cards
    """)
    
    st.markdown("---")
    st.markdown("**Tips for best results:**")
    st.markdown("""
    - Use high-quality images
    - Ensure good lighting
    - Flat, straight images work best
    - For handwriting, print clearly
    """)
    
    st.markdown("---")
    st.markdown("Made with ❤️ by Koshur AI")

# Image upload and preview
col1, col2 = st.columns([1, 2])
with col1:
    st.subheader("Upload Your Image")
    uploaded_file = st.file_uploader(
        "Drag & drop an image here",
        type=["jpg", "jpeg", "png", "bmp", "gif", "tiff", "webp"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", width=300)
        except Exception as e:
            st.error(f"Error loading image: {str(e)}")

with col2:
    st.subheader("Text Extraction Results")
    
    # User options
    extraction_mode = st.radio(
        "Extraction Mode:",
        ["Standard OCR", "Enhanced OCR (for difficult text)"],
        horizontal=True
    )
    
    formatting_options = st.multiselect(
        "Output Formatting:",
        ["Preserve original layout", "Remove line breaks", "Format as paragraphs"],
        default=["Preserve original layout"]
    )
    
    # Response container
    response_container = st.empty()
    
    if st.button("Extract Text", type="primary") and uploaded_file:
        if not api_key:
            st.error("Please enter your OpenRouter API key in the sidebar")
        else:
            try:
                # Convert image to base64
                buffered = io.BytesIO()
                image_format = uploaded_file.type.split('/')[-1].upper()
                if image_format not in ['JPEG', 'PNG']:
                    image_format = 'JPEG'
                image.save(buffered, format=image_format)
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
                
                # Initialize response
                full_response = ""
                response_container = response_container.markdown(full_response, unsafe_allow_html=True)
                
                # Prepare system prompt based on user selections
                system_prompt = """You are a professional OCR (Optical Character Recognition) system. Your task is to:
1. Accurately extract ALL text from the provided image
2. Preserve the original formatting unless instructed otherwise
3. Identify and correct common OCR errors (like '0' vs 'O')
4. Never add or remove text that isn't in the image
5. Clearly indicate any uncertain characters with a [?] symbol

Output rules:
- Return the raw text first in a code block
- Then provide a cleaned version if needed
- Highlight any uncertain characters
- Preserve line breaks and spacing unless instructed otherwise"""
                
                if "Enhanced OCR" in extraction_mode:
                    system_prompt += "\n\nENHANCED MODE: Pay special attention to difficult text, low-quality images, and unusual fonts."
                
                if "Remove line breaks" in formatting_options:
                    system_prompt += "\n\nFORMATTING: Remove unnecessary line breaks and combine into paragraphs where appropriate."
                
                if "Format as paragraphs" in formatting_options:
                    system_prompt += "\n\nFORMATTING: Reformat the text into proper paragraphs with correct punctuation."
                
                # Prepare messages
                messages = [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Extract all text from this image with perfect accuracy:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format.lower()};base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
                
                # Stream the response
                client = get_client(api_key)
                stream = client.chat.completions.create(
                    model="openrouter/optimus-alpha",
                    messages=messages,
                    stream=True
                )
                
                # Display streaming response
                with response_container:
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            st.markdown(f"""
                                <div class="markdown-text">
                                <div class="ocr-output">{full_response}</div>
                                </div>
                            """, unsafe_allow_html=True)
            
            except Exception as e:
                st.error(f"An error occurred during text extraction: {str(e)}")
