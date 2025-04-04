# Gemini Image Editor

A Streamlit web application that uses Google's Gemini Flash 2 model to transform and edit images.

## Features

- **Virtual Try On Tab**: Transform images with style transfer, clothing changes, background modifications, and custom transformations
- **Product Image Editing Tab**: Edit product images with background removal, color changes, effects, quality enhancement, and custom edits

## Installation

### Prerequisites

- Python 3.9+
- UV (for virtual environment and package management)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gemini-images.git
cd gemini-images
```

2. Create a virtual environment and install dependencies using UV:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

3. Configure your API key in one of two ways:

   a. Using Streamlit secrets (recommended):
   ```bash
   # Create the secrets file from the example
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit the file and add your API key
   nano .streamlit/secrets.toml
   ```

   b. Using environment variables:
   ```bash
   # Create and edit .env file
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

Then open your browser and go to `http://localhost:8501`

## How It Works

1. **Upload Images**: Upload one or two images in the appropriate tab
2. **Configure Options**: Select transformation/editing type and adjust settings
3. **Generate**: Click the generate/process button to apply AI transformations
4. **View Results**: See the transformed/edited image displayed in the app

## Dependencies

- streamlit: Web application framework
- google-genai: Google's Generative AI API client
- pillow: Image processing library
- requests: HTTP requests
- python-dotenv: Environment variable management

## License

MIT