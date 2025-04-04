import streamlit as st
import PIL.Image

from app.utils.gemini_client import (
    multi_image_generation,
    extract_response_image,
    extract_response_text,
)


def image_to_image_tab():
    """Streamlit component for image-to-image virtual try on functionality."""

    st.header("Virtual Try On")
    st.write("Upload images and transform them with Gemini Flash 2.")

    # File uploaders
    st.subheader("Upload Images")

    col1, col2 = st.columns(2)

    with col1:
        primary_file = st.file_uploader(
            "Upload primary image (person/product)",
            type=["jpg", "jpeg", "png"],
            key="primary_image",
        )
        if primary_file:
            primary_image = PIL.Image.open(primary_file)
            st.image(primary_image, caption="Primary Image", use_container_width=True)

    with col2:
        secondary_file = st.file_uploader(
            "Upload reference image (optional)",
            type=["jpg", "jpeg", "png"],
            key="secondary_image",
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
                "Virtual try on clothing",
                "Change background",
                "Combine images",
                "Custom",
            ],
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

        elif transformation_type == "Virtual try on clothing":
            if secondary_file:
                prompt = "Show the person in the primary image wearing the clothing from the reference image"
            else:
                clothing = st.text_input(
                    "Describe the clothing", "a black leather jacket with jeans"
                )
                prompt = f"Show the person in the image wearing {clothing}"

        elif transformation_type == "Change background":
            if secondary_file:
                prompt = "Change the background of the primary image to match the style/scene of the reference image"
            else:
                background = st.text_input("Describe the background", "a beach sunset")
                prompt = f"Change the background of the image to {background}"

        elif transformation_type == "Combine images":
            if secondary_file:
                prompt = "Create and generate a new image that combines visual elements from both the primary and reference images. Please return the resulting combined image."
            else:
                st.warning(
                    "Please upload a reference image for this transformation type"
                )
                prompt = "Combine elements from both images into a new generated image"

        else:  # Custom
            prompt = st.text_area(
                "Enter your custom prompt", "Transform these images to..."
            )

        # Generate button
        if st.button("Generate Transformed Image"):
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

                        # Call Gemini API
                        response = multi_image_generation(images, prompt)

                        # For debugging purposes, show response details
                        with st.expander("API Response Details (Debug Info)"):
                            st.text(str(response))

                        # Extract and display response
                        output_image = extract_response_image(response)
                        if output_image:
                            st.image(
                                output_image,
                                caption="Transformed Image",
                                use_container_width=True,
                            )
                        else:
                            output_text = extract_response_text(response)
                            if output_text:
                                st.write("**Model Response:**")
                                st.write(output_text)
                            else:
                                st.write(str(response))
                            st.error("The model didn't return an image.")
                            st.info(
                                "Tips to get better results: \n\n"
                                + "1. Make sure both images are high quality \n"
                                + "2. Try using more specific prompts \n"
                                + "3. Try a different transformation type"
                            )

                    except Exception as e:
                        st.error(f"Error generating transformation: {str(e)}")
                        st.info(
                            "Make sure your Google API key is configured correctly."
                        )
            else:
                st.error("Please upload at least one image to begin.")
    else:
        st.info("Please upload at least one image to begin.")
