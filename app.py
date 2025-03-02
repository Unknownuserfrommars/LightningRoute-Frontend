# frontend/app.py
import streamlit as st
import plotly.graph_objects as go
import json
import openai
from utils import create_mindmap_figure
import platform
import getpass
import os

# import subprocess
# password = "appuser"
# subprocess.run(
#     ["sudo", "-S", "apt-get", "update"],
#     input=password + "\n",  # Provide the password via stdin
#     text=True,              # Treat stdin/stdout as text
# )
# subprocess.run(
#     ["sudo", "-S", "apt-get", "install", "-y", "ffmpeg"],
#     input=password + "\n",  # Provide the password via stdin
#     text=True,              # Treat stdin/stdout as text
# )
# subprocess.run(
#     ["sudo", "-S", "apt-get", "install", "fonts-noto-cjk"],
#     input=password + "\n",  # Provide the password via stdin
#     text=True,              # Treat stdin/stdout as text
# )

def create_directory_from_mindmap(graph_data, base_path):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    
    # Create a mapping of node IDs to their full paths
    node_paths = {}
    nodes = {node['id']: node['label'] for node in graph_data['nodes']}
    
    # First, handle the root node
    root_node = next(node for node in graph_data['nodes'] if node['id'] == 'root')
    root_path = os.path.join(base_path, root_node['label'])
    node_paths['root'] = root_path
    os.makedirs(root_path, exist_ok=True)
    
    # Process all edges to create directory structure
    for edge in graph_data['edges']:
        from_node = edge['from']
        to_node = edge['to']
        
        # If parent path is known
        if from_node in node_paths:
            parent_path = node_paths[from_node]
            child_name = nodes[to_node]
            child_path = os.path.join(parent_path, child_name)
            node_paths[to_node] = child_path
            os.makedirs(child_path, exist_ok=True)
    
    return root_path


# Configure OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Page configuration
st.set_page_config(
    page_title="LightningRoute - AI-Powered Mind Mapping 🧠",
    page_icon="Favicon.png",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Base Theme */
    :root {
        --primary: #FF6B6B;
        --secondary: #4ECDC4;
        --accent: #45B7D1;
        --background: #f8f9fa;
        --text: #2d3436;
    }

    /* Reset container margins */
    .element-container {
        margin: 0 !important;
        padding: 0.5rem 0 !important;
    }

    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 50%, #45B7D1 100%);
        background-attachment: fixed;
    }

    /* Content containers */
    .stTextInput, .stTextArea, .stButton, 
    div[data-testid="stFileUploader"], .stRadio {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 0.7rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(8px);
    }

    /* Button styling */
    .stButton > button {
        width: auto;
        background: linear-gradient(45deg, var(--primary), var(--secondary));
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
        margin: 1rem 0;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    /* Headings */
    h1, h2, h3 {
        color: white;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        padding: 1rem 0;
        margin: 0;
        line-height: 1.4;
    }

    /* Plotly chart container */
    [data-testid="stPlotlyChart"] {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    }

    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.95);
        padding: 2rem 1rem;
    }

    /* File uploader */
    .uploadedFile {
        background: linear-gradient(45deg, var(--secondary), var(--accent));
        border-radius: 8px;
        padding: 0.75rem;
        color: white;
        margin: 0.5rem 0;
    }

    /* Radio buttons */
    .stRadio > div {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }

    /* Debug sections */
    .stTextArea[aria-label="Raw Text Input"],
    .element-container:has(pre) {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        font-family: monospace;
    }

    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .stButton > button {
            width: 100%;
            padding: 0.5rem;
        }
        
        .element-container,
        .stTextInput, .stTextArea,
        div[data-testid="stFileUploader"],
        .stRadio {
            padding: 1rem;
            margin: 0.5rem 0;
        }
    }
</style>
""", unsafe_allow_html=True)
# Main title
st.title("⚡︎ LightningRoute: AI-Powered **Mind Mapping** ⚡︎")

# File upload and text input section
st.subheader("Input Options")
input_type = st.radio("Choose input type:", ["Text Input", "File Upload", "Video URL"])

# Directory creation options
st.subheader("Directory Creation Options")
create_dir = st.radio("Create directory structure from mind map?", ["No", "Yes"])

if create_dir == "Yes":
    # Set default path based on OS
    default_path = "~/" if platform.system() == "Darwin" else f"C:\\Users\\{getpass.getuser()}\\Documents"
    dir_path = st.text_input("Directory path for mind map structure", value=default_path,
                            help="Enter the base directory path where the mind map structure will be created")

text_input = ""

if input_type == "Text Input":
    text_input = st.text_area(
        "Enter your text (e.g., study notes, article, etc.)",
        height=200,
        help="Paste your text here to generate a mind map"
    )
elif input_type == "File Upload":
    uploaded_file = st.file_uploader("Choose a file", type=["txt", "docx", "doc", "pdf", "png", "jpg", "jpeg", "mp3", "mp4"])
    st.caption("If you upload an image, the text will be extracted using OCR.")
    st.caption("Please note that it may take a few minutes for Streamlit cloud to load the model of EasyOCR.")
    st.caption("If you encounter a File Not Found Error (Or similar), please wait a few minutes and retry. If the error persists, contact us at https://github.com/Unknownuserfrommars/LightningRoute-Frontend/issues/")
    if uploaded_file is not None:
        try:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            if uploaded_file.type == "text/plain":
                text_input = uploaded_file.getvalue().decode()
            elif uploaded_file.type == "application/pdf":
                import PyPDF2
                import io
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.getvalue()))
                text_input = ""
                for page in pdf_reader.pages:
                    text_input += page.extract_text()
            elif "word" in uploaded_file.type:
                import docx
                import io
                doc = docx.Document(io.BytesIO(uploaded_file.getvalue()))
                text_input = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            elif uploaded_file.type.startswith("image/"):
                import easyocr
                import numpy as np
                from PIL import Image
                import io
                image = Image.open(io.BytesIO(uploaded_file.getvalue()))
                image_np = np.array(image)
                reader = easyocr.Reader(['en', 'ch_sim'], gpu=False)
                results = reader.readtext(image_np)
                text_lines = [item[1] for item in results]
                text_input = "\n".join(text_lines)
            elif uploaded_file.name.endswith(".mp3"):
                import speech_recognition as sr
                import io
                r = sr.Recognizer()
                audio = sr.AudioFile(io.BytesIO(uploaded_file.getvalue()))
                with audio as source:
                    audio_text = r.record(source)
                    text_input = r.recognize_google(audio_text)
            elif uploaded_file.name.endswith(".mp4"):
                import speech_recognition as sr
                import moviepy.editor as mp
                import io
                video = mp.VideoFileClip(uploaded_file.name)
                audio_f = video.audio
                audio_f.write_audiofile("temp_audio.mp3")
                r = sr.Recognizer()
                with sr.AudioFile("temp_audio.mp3") as source: 
                    data = r.record(source)
                text_input = r.recognize_google(data)
        except Exception as e:
            st.error(f"Error reading file: {str(e)}")
else:
    video_url = st.text_area(
        "Enter your video URL",
        height=100,
        help="MUST BE FULL URL!!!"
    )
    try:
        import yt_dlp
        from pydub import AudioSegment
        import speech_recognition as sr
        ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': 'audio.mp3'
        }
        # import shutil

        # ffmpeg_path = shutil.which("ffmpeg")
        # ffprobe_path = shutil.which("ffprobe")
        # st.text(ffmpeg_path)
        # st.text(ffprobe_path)
    
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        audio_download_path = os.path.join(os.getcwd(), 'audio.mp3')
        audio = AudioSegment.from_file(audio_download_path, format="mp3")
        wav_path = audio_download_path.replace(".mp3", ".wav")
        recognizer = sr.Recognizer()

        with sr.AudioFile() as source:
            print("🔊 Extracting audio...")
            audio_data = recognizer.record(source)

            try:
                print("📝 Converting audio to text...")
                text_input = recognizer.recognize_google(audio_data, language="zh-CN")
            except sr.UnknownValueError:
                raise ValueError("Cannot recognize the audio")
            except sr.RequestError:
                raise ConnectionError("Unable to connect Google API")
        
        if os.path.exists(audio_download_path):
            os.remove(audio_download_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

    except Exception as e:
        st.error(f"Error reading video: {str(e)}")

col1, col2 = st.columns([2,10])
# Process button
if col1.button("Generate Mind Map"):
    if text_input:
        with st.spinner("Generating mind map..."):
            try:
                # Call OpenAI API to process the text and generate mind map structure
                prompt = f"""Given the following text, create a mind map structure. Extract key concepts and their relationships.
                Format the response as a JSON with two arrays:
                1. 'nodes': Each node has 'id' (unique string) and 'label' (displayed text)
                2. 'edges': Each edge has 'from' and 'to' node IDs showing relationships
                Root node should have id 'root'. Example format:
                {{
                    "nodes": [{{"id": "root", "label": "Main Topic"}}, {{"id": "1", "label": "Subtopic"}}],
                    "edges": [{{"from": "root", "to": "1"}}]
                }}
                
                Text to analyze:
                {text_input}
                """
                # TODO: Add option for "New learners" and "Experienced learners" to the button
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=[{
                        "role": "system",
                        "content": "You are a mind map generator that converts text into structured mind maps."
                    }, {
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                # Extract and parse the JSON response
                try:
                    gpt_response = response.choices[0].message.content
                    # Debug: Show GPT's raw response
                    # st.subheader("Debug: GPT Response")
                    # st.text(gpt_response)
                    #print(gpt_response)
                    
                    # Parse the JSON response
                    gpt_response_trimmed = gpt_response.strip().replace("```json", "").replace("```", "").strip()
                    graph_data = json.loads(gpt_response_trimmed)
                except Exception as e:
                    st.error(f"An error has occured while GPT is responding: {e}")
                # Debug: Print raw text input
                # st.subheader("Debug: Input Text")
                # st.text_area("Raw Text Input", text_input, height=100)
                
                # Debug: Print graph data
                # st.subheader("Debug: Graph Data")
                # st.json(graph_data)
                
                # Create and display mind map
                st.subheader("Mind Map Visualization")
                fig = create_mindmap_figure(graph_data)
                fig.update_layout(font=dict(family="Noto Sans CJK", size=12, color="black"))
                st.plotly_chart(fig, use_container_width=True)
                
                # Add download button for the mind map
                st.download_button(
                    "Download Mindmap as JSON",
                    data=json.dumps(graph_data),
                    file_name="mindmap.json",
                    mime="application/json"
                )

                img_bytes = fig.to_image(format="png")
                st.download_button(
                label="Download Mindmap as PNG",
                data=img_bytes,
                file_name="plotly_chart.png",
                mime="image/png"
                )
                
                if create_dir == "Yes":
                    try:
                        # Expand the path if it contains ~
                        expanded_path = os.path.expanduser(dir_path)
                        # Create directory structure
                        root_dir = create_directory_from_mindmap(graph_data, expanded_path)
                        st.success(f"Successfully created directory structure at: {root_dir}")
                    except Exception as e:
                        st.error(f"Error creating directory structure: {str(e)}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter some text or upload a file to generate a mind map.")

# Add instructions in sidebar
with st.sidebar:
    st.header("How to use LightningRoute⚡")
    st.markdown("""
   1. Paste your text in the input area / Upload a file (PDF, DOCX, TXT) / Upload a picture / Enter a video URL
    2. Choose whether to get a structured file directory or not
    3. Click 'Generate Mind Map'
    4. Interact with the mind map:
        - Zoom in/out
        - Fullscreen
    5. Download the mind map (as JSON or PNG) for later use
    """)
