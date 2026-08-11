import streamlit as st
import requests
from io import BytesIO

st.set_page_config(page_title='NIKO TEST', layout='centered')

st.title('🎤 ElevenLabs Test')

script = st.text_area('Metin', 'Merhaba Niko')
api_key = st.text_input('API Key', type='password')
voice_id = st.text_input('Voice ID')

if st.button('Ses Oluştur'):
    if not api_key or not voice_id:
        st.error('API key ve Voice ID gir')
    else:
        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'

        r = requests.post(
            url,
            headers={
                'xi-api-key': api_key,
                'Content-Type': 'application/json'
            },
            json={
                'text': script,
                'model_id': 'eleven_multilingual_v2'
            }
        )

        if r.status_code == 200:
            st.success('Başarılı')
            st.audio(r.content, format='audio/mp3')

            st.download_button(
                'MP3 İndir',
                data=BytesIO(r.content),
                file_name='ses.mp3',
                mime='audio/mpeg'
            )
        else:
            st.error(r.text)