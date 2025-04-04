import streamlit as st
import PIL.Image

from app.utils.gemini_client import (
    multi_image_generation,
    extract_response_image,
    extract_response_text,
)


def image_to_image_tab():
    """Streamlit component for virtual try-on functionality."""

    st.header("Virtual Try On")
    st.write("See how clothing items would look on a person.")

    # File uploaders
    st.subheader("Upload Images")

    col1, col2 = st.columns(2)

    with col1:
        primary_file = st.file_uploader(
            "Upload image of a person",
            type=["jpg", "jpeg", "png"],
            key="tryon_person",
        )
        if primary_file:
            primary_image = PIL.Image.open(primary_file)
            st.image(primary_image, caption="Person Image", use_container_width=True)

    with col2:
        clothing_file = st.file_uploader(
            "Upload clothing image (optional)",
            type=["jpg", "jpeg", "png"],
            key="tryon_clothing",
        )
        if clothing_file:
            clothing_image = PIL.Image.open(clothing_file)
            st.image(clothing_image, caption="Clothing Image", use_container_width=True)

    # Try-on options
    if primary_file is not None:
        st.subheader("Clothing Options")

        if not clothing_file:
            clothing_type = st.selectbox(
                "Clothing type",
                [
                    "Casual outfit",
                    "Formal outfit",
                    "Sportswear",
                    "Costume",
                    "Custom",
                ],
            )

            if clothing_type == "Custom":
                clothing = st.text_input(
                    "Describe the clothing", "a black leather jacket with jeans"
                )
            else:
                clothing_descriptions = {
                    "Casual outfit": "casual jeans and t-shirt outfit",
                    "Formal outfit": "formal business suit or dress",
                    "Sportswear": "athletic wear, gym outfit",
                    "Costume": "Halloween or themed costume",
                }
                clothing = clothing_descriptions[clothing_type]

            prompt = f"Show the person in the image wearing {clothing}"
        else:
            prompt = "Show the person in the primary image wearing the clothing from the reference image"

        # Additional instructions
        st.subheader("Custom Instructions")
        additional_instructions = st.text_area(
            "Add any additional try-on instructions (optional)",
            "",
            key="additional_tryon_instructions",
        )

        if additional_instructions:
            prompt += f" Additionally: {additional_instructions}"

        # Generate button
        if st.button("Generate Try-On Image"):
            if primary_file:
                with st.spinner("Generating virtual try-on..."):
                    try:
                        # Get image bytes from uploaded files
                        primary_file.seek(0)
                        primary_bytes = primary_file.read()

                        images = [primary_bytes]

                        if clothing_file:
                            clothing_file.seek(0)
                            clothing_bytes = clothing_file.read()
                            images.append(clothing_bytes)

                        # Call Gemini API
                        response = multi_image_generation(images, prompt)

                        # Extract and display response
                        output_image = extract_response_image(response)
                        if output_image:
                            st.image(
                                output_image,
                                caption="Virtual Try-On Result",
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
                                + "1. Make sure the person is clearly visible \n"
                                + "2. Try using more specific clothing descriptions \n"
                                + "3. Use high quality reference clothing images"
                            )

                    except Exception as e:
                        st.error(f"Error generating try-on: {str(e)}")
                        st.info(
                            "Make sure your Google API key is configured correctly."
                        )
            else:
                st.error("Please upload an image of a person to begin.")
    else:
        st.info("Please upload an image of a person to begin.")
