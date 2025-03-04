from config import LOGO_STYLE_HTML
from PIL import Image
import base64
from pathlib import Path
import logging
import streamlit as st
import os

def resize_image(image_path: str, target_height: int):
    img = Image.open(image_path)
    width, height = img.size

    new_width = int((target_height/height)*width)
    img = img.resize((new_width, target_height))

    return img

def img_to_bytes(img_path):
    try:
        img_bytes = Path(img_path).read_bytes()
        encoded = base64.b64encode(img_bytes).decode()
        return encoded

    except Exception as ex:
        logging.error(f'Error in img_to_bytes: {ex}')
        return None

def img_to_html(img_path):
    try:
        img_html = f"<img src='data:image/png;base64,{img_to_bytes(img_path)}' class='img-fluid' id='fixed-image'>"
        return img_html

    except Exception as ex:
        logging.error(f'Error in img_to_html: {ex}')
        return None

def display_images():
    try:
        col1, col2 = st.columns(2)

        with open(LOGO_STYLE_HTML) as f:
            st.markdown(f.read(), unsafe_allow_html=True)

        with col1:
            image_path_1 = os.path.join(os.getcwd(),'static', 'images', 'CMS.png')
            st.markdown(img_to_html(image_path_1), unsafe_allow_html=True)
        
        with col2:
            image_path_2 = os.path.join(os.getcwd(),'static', 'images', 'BAT.png')
            st.markdown(img_to_html(image_path_2), unsafe_allow_html=True)

    except Exception as ex:
        logging.error(f'Error in display_image_and_intro: {ex}')
        return None