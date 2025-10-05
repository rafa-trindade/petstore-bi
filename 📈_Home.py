import streamlit as st
import src.utils as util

st.set_page_config(
    layout="wide",
    page_title="petStore BI", 
    initial_sidebar_state="expanded", 
    page_icon="📊")

util.aplicar_estilo()

sidebar_logo = "https://i.postimg.cc/fWBrwgQt/logo-pettore.png"
main_body_logo = "https://i.postimg.cc/3xkGPmC6/streamlit02.png"
st.logo(sidebar_logo, icon_image=main_body_logo)











st.markdown(
    """
    <div style="
        position: fixed; 
        bottom: 0;
        left: 0;
        right: 0; 
        width: 100%; 
        background-color: #c6d0d2; 
        padding: 2.5px; 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        color: #6282A3; 
        font-size: 14px;
        gap: 8px;
    ">
        <span>Developed by </span>
        <a href="https://github.com/rafa-trindade" target="_blank">
            <img src="https://img.shields.io/badge/-Rafael%20Trindade-6282A3?style=flat-square&logo=github&logoColor=E4E3E3" alt="GitHub Badge">
        </a>
    </div>

    """,
    unsafe_allow_html=True
)