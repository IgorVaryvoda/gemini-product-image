import streamlit as st
import PIL.Image

from app.utils.gemini_client import (
    image_to_image_generation,
    multi_image_generation,
    extract_response_image,
    extract_response_text,
)


def product_editing_tab():
    """Streamlit component for product image editing functionality."""

    st.header("Product Image Editing")
    st.write("Upload a product image and refine it with Gemini Flash 2.")

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
            prompt = "Remove the background from this product image and replace it with a clean white background."

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
                prompt = "Remove the background from the first product image and place it on the background from the second image. Make it look natural and well-integrated."
            else:
                prompt = "Remove the background from this product image and replace it with a clean white background."
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
            prompt = "Enhance this product image: increase resolution, improve lighting, and make it look professional."

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

                    # Call Gemini API
                    if editing_type == "Replace background" and background_file:
                        background_file.seek(0)
                        background_bytes = background_file.read()

                        # Use multi-image generation function
                        response = multi_image_generation(
                            [image_bytes, background_bytes], prompt
                        )
                    else:
                        # Use single image generation function
                        response = image_to_image_generation(image_bytes, prompt)

                    # Extract and display response
                    output_image = extract_response_image(response)
                    if output_image:
                        st.image(
                            output_image,
                            caption="Edited Product Image",
                            use_container_width=True,
                        )
                    else:
                        output_text = extract_response_text(response)
                        if output_text:
                            st.write("**Model Response:**")
                            st.write(output_text)
                        else:
                            st.write("No image was generated.")
                        st.error("The model didn't return an image.")
                        st.info(
                            "Tips to get better results: \n\n"
                            + "1. Make sure images are high quality \n"
                            + "2. Try using more specific prompts \n"
                            + "3. Try a different editing operation"
                        )
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")
                    st.info("Make sure your Google API key is configured correctly.")
    else:
        st.info("Please upload a product image to begin.")
