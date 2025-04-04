import streamlit as st
from app.components.image_to_image import image_to_image_tab
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
    - Virtual Try On: Transform images with style transfer, clothing changes, and more
    - Product Image Editing: Edit product images for commercial use
    """)

    # Create tabs
    tab1, tab2 = st.tabs(["Virtual Try On", "Product Image Editing"])

    # Tab content
    with tab1:
        image_to_image_tab()

    with tab2:
        product_editing_tab()

    # Sidebar
    with st.sidebar:
        st.subheader("How It Works")
        st.markdown("""
        ### 1. Choose a Tab
        - **Virtual Try On**: Transform images and combine multiple photos
        - **Product Image Editing**: Polish and enhance product photos

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
