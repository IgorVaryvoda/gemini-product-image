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
        st.subheader("About")
        st.markdown("""
        This app uses Google's Gemini Flash 2 model to transform and edit images.

        **API Key Configuration:**
        You can set your Google API key in either:

        1. `.streamlit/secrets.toml` file:
        ```
        GOOGLE_API_KEY = "your_api_key_here"
        ```

        2. Or in a `.env` file:
        ```
        GOOGLE_API_KEY=your_api_key_here
        ```
        """)

        st.subheader("Options")
        st.checkbox("Enable high quality (may be slower)", value=False)

        # Add credits
        st.markdown("---")
        st.caption("Built with Streamlit and Google Generative AI")


if __name__ == "__main__":
    main()
