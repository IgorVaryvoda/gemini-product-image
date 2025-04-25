import os
import base64
from io import BytesIO
from typing import List, Union

import PIL.Image
import requests
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Load environment variables
load_dotenv()


# Get API key (prioritize Streamlit secrets over .env)
def get_api_key():
    """Get API key from Streamlit secrets or environment variables."""
    if hasattr(st, "secrets") and "OPENAI_API_KEY" in st.secrets:
        return st.secrets["OPENAI_API_KEY"]
    return os.getenv("OPENAI_API_KEY")


def process_image(image: Union[str, PIL.Image.Image, bytes]):
    """Process different image input types for OpenAI API.

    Args:
        image: Can be a path string, PIL Image object, or bytes.

    Returns:
        Processed image in bytes format for OpenAI API.
    """
    if isinstance(image, str):
        # Check if it's a URL
        if image.startswith(("http://", "https://")):
            response = requests.get(image)
            return response.content
        # Assume it's a file path
        with open(image, "rb") as f:
            return f.read()
    elif isinstance(image, PIL.Image.Image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return buffer.getvalue()
    elif isinstance(image, bytes):
        return image
    else:
        raise TypeError(
            "Unsupported image type. Must be path string, PIL Image, or bytes."
        )


def image_to_image_generation(image, prompt, model="gpt-image-1", size="1024x1024"):
    """Generate a transformed image based on a source image and prompt."""
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)

    # Process the image
    processed_image = process_image(image)

    # Convert bytes to file-like object with proper MIME type
    import io

    img_obj = io.BytesIO(processed_image)
    img_obj.name = "image.png"  # Set a filename with extension

    try:
        # Use edit endpoint for a single image transformation
        result = client.images.edit(
            model=model, image=img_obj, prompt=prompt, size=size
        )
        return result
    except Exception as e:
        st.error(f"Error with OpenAI image edit: {str(e)}")
        return None


def multi_image_generation(
    images_list: List, prompt, model="gpt-image-1", size="1024x1024"
):
    """Generate content based on multiple images and a prompt using OpenAI."""
    api_key = get_api_key()
    client = OpenAI(api_key=api_key)

    processed_images = [process_image(img) for img in images_list]

    # If there are multiple images, use the edit endpoint
    if len(processed_images) > 1:
        try:
            # Convert bytes to file-like objects with proper MIME type
            import io

            # Prepare image objects as a list
            image_objects = []
            for i, img_bytes in enumerate(processed_images):
                img_obj = io.BytesIO(img_bytes)
                img_obj.name = f"image_{i}.png"  # Set filename with extension
                image_objects.append(img_obj)

            # Call the edit endpoint with multiple images
            result = client.images.edit(
                model=model,
                image=image_objects,  # Pass list of file-like objects
                prompt=prompt,
                size=size,
            )
        except Exception as e:
            st.error(f"Error with OpenAI image edit: {str(e)}")
            return None
    else:
        # For single image with OpenAI, we still use the edit endpoint
        # instead of generate to respect the input image
        try:
            return image_to_image_generation(
                processed_images[0], prompt, model=model, size=size
            )
        except Exception as e:
            st.error(f"Error with OpenAI image processing: {str(e)}")
            return None

    return result


def extract_response_image(response):
    """Extract image from OpenAI response."""
    # Guard against None response
    if response is None:
        return None

    try:
        # Get the b64_json from the first image in the response
        has_data = hasattr(response, "data") and response.data
        if has_data and hasattr(response.data[0], "b64_json"):
            image_base64 = response.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            return PIL.Image.open(BytesIO(image_bytes))
        elif has_data and hasattr(response.data[0], "url"):
            # If URL is provided instead of base64 content
            response = requests.get(response.data[0].url)
            return PIL.Image.open(BytesIO(response.content))
    except Exception as e:
        st.error(f"Error extracting image from OpenAI response: {str(e)}")

    return None


def extract_response_text(response):
    """Extract text from OpenAI response if available."""
    # OpenAI image responses don't typically include text
    return None
