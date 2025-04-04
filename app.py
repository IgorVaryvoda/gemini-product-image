import streamlit as st
from app.components.image_to_image import image_to_image_tab
from app.components.style_transfer import style_transfer_tab
from app.components.product_editing import product_editing_tab

# Set page config
st.set_page_config(
    page_title="Gemini Image Editor",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Main app
def main():
    # App title and description
    st.title("Gemini Image Editor")
    st.markdown("""
    Transform and edit images using Google's Gemini Flash 2 AI model.

    **Features:**
    - Virtual Try On: See how clothing would look on a person
    - Image Transformations: Apply style transfer and other effects
    - Product Editing: Enhance product images for commercial use
    """)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(
        ["Virtual Try On", "Image Transformations", "Product Editing"]
    )

    # Tab content
    with tab1:
        image_to_image_tab()

    with tab2:
        style_transfer_tab()

    with tab3:
        product_editing_tab()

    # Sidebar
    with st.sidebar:
        st.subheader("How It Works")
        st.markdown("""
        ### 1. Choose a Tab
        - **Virtual Try On**: Try clothes on a person
        - **Image Transformations**: Style transfer and image edits
        - **Product Editing**: Enhance product photos

        ### 2. Upload Image(s)
        Upload one or more images to work with

        ### 3. Select Options
        Choose transformation types and customize settings

        ### 4. Generate
        Click the button to process your images with AI
        """)

        # Add credits
        st.markdown("---")
        st.caption("Built with Streamlit and Google Gemini")


if __name__ == "__main__":
    main()
