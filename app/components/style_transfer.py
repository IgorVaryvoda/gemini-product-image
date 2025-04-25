import streamlit as st
import PIL.Image

from app.utils.gemini_client import (
    multi_image_generation as gemini_multi_image_generation,
    extract_response_image as gemini_extract_response_image,
    extract_response_text as gemini_extract_response_text,
)
from app.utils.openai_client import (
    multi_image_generation as openai_multi_image_generation,
    extract_response_image as openai_extract_response_image,
    extract_response_text as openai_extract_response_text,
)


def style_transfer_tab():
    """Streamlit component for general image transformations."""

    st.header("Image Transformations")
    st.write("Apply style transfer and other transformations to your images.")

    # Model selection
    st.subheader("Model Selection")
    model_provider = st.selectbox(
        "Select AI provider", ["Google Gemini", "OpenAI"], key="style_provider"
    )

    if model_provider == "Google Gemini":
        gemini_models = ["gemini-2.0-flash-exp-image-generation"]
        model_name = st.selectbox(
            "Select Gemini model", gemini_models, key="style_gemini_model"
        )
    else:  # OpenAI
        openai_models = ["gpt-image-1"]
        model_name = st.selectbox(
            "Select OpenAI model", openai_models, key="style_openai_model"
        )
        size_options = ["1024x1024", "1536x1024", "1024x1536"]
        image_size = st.selectbox("Image size", size_options, key="style_size")

    # File uploaders
    st.subheader("Upload Images")

    col1, col2 = st.columns(2)

    with col1:
        primary_file = st.file_uploader(
            "Upload primary image",
            type=["jpg", "jpeg", "png"],
            key="primary_image_style",
        )
        if primary_file:
            primary_image = PIL.Image.open(primary_file)
            st.image(primary_image, caption="Primary Image", use_container_width=True)

    with col2:
        secondary_file = st.file_uploader(
            "Upload reference image (optional)",
            type=["jpg", "jpeg", "png"],
            key="secondary_image_style",
        )
        if secondary_file:
            secondary_image = PIL.Image.open(secondary_file)
            st.image(
                secondary_image, caption="Reference Image", use_container_width=True
            )

    # Transformation options
    if primary_file is not None:
        st.subheader("Transformation Options")

        transformation_type = st.selectbox(
            "Select transformation type",
            [
                "Style transfer",
                "Change background",
                "Combine images",
                "Custom",
            ],
            key="style_transform_type",
        )

        # Custom prompt based on transformation type
        if transformation_type == "Style transfer":
            prompt_template = "Transform the primary image in the style of {}"
            style = st.selectbox(
                "Select style",
                [
                    "impressionism",
                    "watercolor",
                    "pop art",
                    "cyberpunk",
                    "anime",
                    "sketch",
                ],
            )
            prompt = prompt_template.format(style)

        elif transformation_type == "Change background":
            if secondary_file:
                prompt = (
                    "Change the background of the primary image to match "
                    "the style/scene of the reference image"
                )
            else:
                background = st.text_input(
                    "Describe the background", "a beach sunset", key="bg_style"
                )
                prompt = f"Change the background of the image to {background}"

        elif transformation_type == "Combine images":
            if secondary_file:
                prompt = (
                    "Create and generate a new image that combines visual "
                    "elements from both the primary and reference images. "
                    "Please return the resulting combined image."
                )
            else:
                st.warning(
                    "Please upload a reference image for this transformation type"
                )
                prompt = "Combine elements from both images into a new generated image"

        else:  # Custom
            prompt = st.text_area(
                "Enter your custom prompt",
                "Transform these images to...",
                key="custom_style",
            )

        # Additional instructions
        st.subheader("Custom Instructions")
        additional_instructions = st.text_area(
            "Add any additional transformation instructions (optional)",
            "",
            key="additional_style_instructions",
        )

        if additional_instructions:
            prompt += f" Additionally: {additional_instructions}"

        # Generate button
        if st.button("Generate Transformed Image", key="style_button"):
            if primary_file:
                with st.spinner("Generating image transformation..."):
                    try:
                        # Get image bytes from uploaded files
                        primary_file.seek(0)
                        primary_bytes = primary_file.read()

                        images = [primary_bytes]

                        if secondary_file:
                            secondary_file.seek(0)
                            secondary_bytes = secondary_file.read()
                            images.append(secondary_bytes)

                        # Call the selected API
                        if model_provider == "Google Gemini":
                            response = gemini_multi_image_generation(
                                images, prompt, model=model_name
                            )
                            output_image = gemini_extract_response_image(response)
                            output_text = gemini_extract_response_text(response)
                        else:  # OpenAI
                            response = openai_multi_image_generation(
                                images, prompt, model=model_name, size=image_size
                            )
                            output_image = openai_extract_response_image(response)
                            output_text = openai_extract_response_text(response)

                        # Display response
                        if output_image:
                            st.image(
                                output_image,
                                caption="Transformed Image",
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
                                "1. Make sure both images are high quality \n"
                                "2. Try using more specific prompts \n"
                                "3. Try a different transformation type"
                            )
                            st.info(tips)

                    except Exception as e:
                        st.error(f"Error generating transformation: {str(e)}")
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
                st.error("Please upload at least one image to begin.")
    else:
        st.info("Please upload at least one image to begin.")
