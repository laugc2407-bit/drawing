import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from streamlit_drawable_canvas import st_canvas

# Variables globales
Expert = " "
profile_imgenh = " "

# Función para convertir imagen a base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return None

# Configuración de la app
st.set_page_config(page_title='Tablero Inteligente')
st.title('Tablero Inteligente')

# Sidebar
with st.sidebar:
    st.subheader("Dibuja en el tablero y deja que lo analicemos")
    stroke_width = st.slider('Selecciona el ancho de línea', 1, 30, 5)
    ke = st.text_input('Ingresa tu Clave', type="password")

# Configuración de dibujo
drawing_mode = "freedraw"
stroke_color = "#000000"
bg_color = "#FFFFFF"

# Canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

# API Key
if ke:
    os.environ['OPENAI_API_KEY'] = ke
    api_key = ke
else:
    api_key = None

# Cliente OpenAI
client = None
if api_key:
    client = OpenAI(api_key=api_key)

# Botón
analyze_button = st.button("Analizar", type="secondary")

# Lógica principal
if canvas_result.image_data is not None and api_key and analyze_button:

    with st.spinner("Analizando ..."):
        # Convertir imagen
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')

        base64_image = encode_image_to_base64("img.png")

        if base64_image is None:
            st.error("Error al procesar la imagen.")
        else:
            prompt_text = "Describe en español brevemente la imagen"

            try:
                message_placeholder = st.empty()

                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=500,
                )

                if response.choices[0].message.content:
                    full_response = response.choices[0].message.content
                    message_placeholder.markdown(full_response)

                    if Expert == profile_imgenh:
                        st.session_state.mi_respuesta = full_response

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")

else:
    if not api_key:
        st.warning("¿Ya ingresaste tu API Key?")
