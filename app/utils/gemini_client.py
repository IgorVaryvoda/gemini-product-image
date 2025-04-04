import os
import pathlib
from typing import Union, List
import requests
from io import BytesIO

from google import genai
from google.genai import types
import PIL.Image
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()


# Get API key (prioritize Streamlit secrets over .env)
def get_api_key():
    """Get API key from Streamlit secrets or environment variables."""
    if hasattr(st, "secrets") and "GOOGLE_API_KEY" in st.secrets:
        return st.secrets["GOOGLE_API_KEY"]
    return os.getenv("GOOGLE_API_KEY")


def process_image(image: Union[str, PIL.Image.Image, bytes]):
    """Process different image input types for Gemini API.

    Args:
        image: Can be a path string, PIL Image object, or bytes.

    Returns:
        Processed image ready for Gemini API.
    """
    if isinstance(image, str):
        # Check if it's a URL
        if image.startswith(("http://", "https://")):
            response = requests.get(image)
            return response.content
        # Assume it's a file path
        return types.Part.from_bytes(
            data=pathlib.Path(image).read_bytes(), mime_type="image/jpeg"
        )
    elif isinstance(image, PIL.Image.Image):
        return image
    elif isinstance(image, bytes):
        return types.Part.from_bytes(data=image, mime_type="image/jpeg")
    else:
        raise TypeError(
            "Unsupported image type. Must be path string, PIL Image, or bytes."
        )


def image_to_image_generation(
    source_image, prompt, model="gemini-2.0-flash-exp-image-generation"
):
    """Generate a transformed image based on a source image and prompt."""

    processed_image = process_image(source_image)
    api_key = get_api_key()

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=[prompt, processed_image],
        config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
    )

    return response


def multi_image_generation(
    images_list: List, prompt, model="gemini-2.0-flash-exp-image-generation"
):
    """Generate content based on multiple images and a prompt."""
    processed_images = [process_image(img) for img in images_list]
    api_key = get_api_key()

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=[prompt, *processed_images],
        config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
    )

    return response


def extract_response_image(response):
    """Extract image from Gemini response."""
    # Guard against None response
    if response is None:
        return None

    try:
        # Check for candidates in response
        if hasattr(response, "candidates") and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, "content") and candidate.content:
                    for part in candidate.content.parts:
                        # Check for inline_data Blob
                        if hasattr(part, "inline_data") and part.inline_data:
                            if hasattr(
                                part.inline_data, "mime_type"
                            ) and part.inline_data.mime_type.startswith("image/"):
                                return PIL.Image.open(BytesIO(part.inline_data.data))
                            # Handle Blob data without mime_type
                            elif hasattr(part.inline_data, "data"):
                                try:
                                    return PIL.Image.open(
                                        BytesIO(part.inline_data.data)
                                    )
                                except Exception:
                                    pass
    except Exception as e:
        st.error(f"Error extracting image from response: {str(e)}")

    return None


def extract_response_text(response):
    """Extract text from Gemini response."""
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "text") and part.text:
                return part.text
    return None
