import streamlit as st
import PIL.Image

from app.utils.gemini_client import (
    image_to_image_generation as gemini_image_generation,
    multi_image_generation as gemini_multi_image_generation,
    extract_response_image as gemini_extract_response_image,
    extract_response_text as gemini_extract_response_text,
)
from app.utils.openai_client import (
    image_to_image_generation as openai_image_generation,
    multi_image_generation as openai_multi_image_generation,
    extract_response_image as openai_extract_response_image,
    extract_response_text as openai_extract_response_text,
)


def product_editing_tab():
    """Streamlit component for product image editing functionality."""

    st.header("Product Image Editing")
    st.write("Upload a product image and refine it with AI.")

    # Model selection
    st.subheader("Model Selection")
    model_provider = st.selectbox(
        "Select AI provider", ["Google Gemini", "OpenAI"], key="product_provider"
    )

    if model_provider == "Google Gemini":
        gemini_models = ["gemini-2.0-flash-preview-image-generation"]
        model_name = st.selectbox(
            "Select Gemini model", gemini_models, key="product_gemini_model"
        )
    else:  # OpenAI
        openai_models = ["gpt-image-1"]
        model_name = st.selectbox(
            "Select OpenAI model", openai_models, key="product_openai_model"
        )
        size_options = ["1024x1024", "1536x1024", "1024x1536"]
        image_size = st.selectbox("Image size", size_options, key="product_size")

    # File uploader for main product image
    uploaded_file = st.file_uploader(
        "Upload product image", type=["jpg", "jpeg", "png"], key="product_image"
    )

    if uploaded_file is not None:
        # Display the uploaded image
        image = PIL.Image.open(uploaded_file)
        st.image(image, caption="Original Product Image", use_container_width=True)

        # Editing options
        st.subheader("Editing Options")

        editing_type = st.selectbox(
            "Select editing operation",
            [
                "Background removal",
                "Replace background",
                "Change product color",
                "Add effects/filters",
                "Enhance quality",
                "Custom edit",
            ],
        )

        # Custom prompt based on editing type
        if editing_type == "Background removal":
            prompt = (
                "Remove the background from this product image and replace "
                "it with a clean white background."
            )

        elif editing_type == "Replace background":
            # Add background image uploader
            background_file = st.file_uploader(
                "Upload background image",
                type=["jpg", "jpeg", "png"],
                key="background_image",
            )

            if background_file:
                # Display the background image
                background_image = PIL.Image.open(background_file)
                st.image(
                    background_image,
                    caption="Background Image",
                    use_container_width=True,
                )
                prompt = (
                    "Remove the background from the first product image and "
                    "place it on the background from the second image. Make "
                    "it look natural and well-integrated."
                )
            else:
                prompt = (
                    "Remove the background from this product image and "
                    "replace it with a clean white background."
                )
                st.info("Upload a background image to replace the product background.")

        elif editing_type == "Change product color":
            color = st.color_picker("Select new color", "#00BFFF")
            prompt = f"Change the color of this product to {color}."

        elif editing_type == "Add effects/filters":
            effect = st.selectbox(
                "Select effect/filter",
                [
                    "soft shadow",
                    "glossy reflection",
                    "dramatic lighting",
                    "studio lighting",
                    "minimalist",
                ],
            )
            prompt = f"Apply a {effect} effect to this product image."

        elif editing_type == "Enhance quality":
            prompt = (
                "Enhance this product image: increase resolution, improve "
                "lighting, and make it look professional."
            )

        else:  # Custom edit
            prompt = st.text_area(
                "Enter your custom editing instructions",
                "Edit this product image to...",
                key="custom_product",
            )

        # Additional options
        st.subheader("Additional Settings")

        maintain_proportions = st.checkbox("Maintain original proportions", value=True)
        if not maintain_proportions:
            aspect_ratio = st.select_slider(
                "Select aspect ratio",
                options=["1:1 (square)", "4:3", "16:9", "3:2", "2:3 (portrait)"],
                value="1:1 (square)",
            )
            prompt += f" Output the image in {aspect_ratio} aspect ratio."

        # Additional customization instructions
        st.subheader("Custom Instructions")
        additional_instructions = st.text_area(
            "Add any additional editing instructions (optional)",
            "",
            key="additional_instructions",
        )

        if additional_instructions:
            prompt += f" Additionally: {additional_instructions}"

        # Generate button
        if st.button("Process Product Image"):
            with st.spinner("Processing image..."):
                try:
                    # Get image bytes from uploaded file
                    uploaded_file.seek(0)
                    image_bytes = uploaded_file.read()

                    # Prepare images list
                    images = [image_bytes]

                    if editing_type == "Replace background" and background_file:
                        background_file.seek(0)
                        background_bytes = background_file.read()
                        images.append(background_bytes)

                    # Call the selected API
                    if model_provider == "Google Gemini":
                        if len(images) > 1:
                            response = gemini_multi_image_generation(
                                images, prompt, model=model_name
                            )
                        else:
                            response = gemini_image_generation(
                                images[0], prompt, model=model_name
                            )
                        output_image = gemini_extract_response_image(response)
                        output_text = gemini_extract_response_text(response)
                    else:  # OpenAI
                        if len(images) > 1:
                            response = openai_multi_image_generation(
                                images, prompt, model=model_name, size=image_size
                            )
                        else:
                            response = openai_image_generation(
                                images[0], prompt, model=model_name, size=image_size
                            )
                        output_image = openai_extract_response_image(response)
                        output_text = openai_extract_response_text(response)

                    # Display response
                    if output_image:
                        st.image(
                            output_image,
                            caption="Edited Product Image",
                            use_container_width=True,
                        )
                    else:
                        if output_text:
                            st.write("**Model Response:**")
                            st.write(output_text)
                        else:
                            st.write("No image was generated.")
                        st.error("The model didn't return an image.")
                        tips = (
                            "Tips to get better results: \n\n"
                            "1. Make sure images are high quality \n"
                            "2. Try using more specific prompts \n"
                            "3. Try a different editing operation"
                        )
                        st.info(tips)
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    if model_provider == "Google Gemini":
                        api_key_msg = (
                            "Make sure your Google API key is configured correctly."
                        )
                    else:
                        api_key_msg = (
                            "Make sure your OpenAI API key is configured correctly."
                        )
                    st.info(api_key_msg)
    else:
        st.info("Please upload a product image to begin.")
