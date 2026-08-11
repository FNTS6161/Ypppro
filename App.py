import streamlit as st
import requests
from io import BytesIO

st.set_page_config(page_title='NIKO VIDEO FACTORY', layout='centered')

st.title('🎬 NIKO VIDEO FACTORY')
st.caption('ElevenLabs ses üretim test uygulaması')

script = st.text_area('Senaryo', height=180, placeholder='Videoda okunacak metni yaz...')
api_key = st.text_input('ElevenLabs API Key', type='password')
voice_id = st.text_input('Voice ID')

fmt = st.radio('Format', ['Shorts 9:16', 'Long 16:9'], horizontal=True)

mirror = st.checkbox('Aynalama')
emoji = st.checkbox('Emoji ekle', value=True)
glow = st.checkbox('Glow efekti', value=True)

if st.button('🚀 Ses Oluştur', use_container_width=True):
    if not script or not api_key or not voice_id:
        st.error('Lütfen senaryo, API key ve Voice ID gir.')
    else:
        text = ('🔥 ' if emoji else '') + script

        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'
        headers = {
            'xi-api-key': api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'text': text,
            'model_id': 'eleven_multilingual_v2'
        }

        with st.spinner('ElevenLabs sesi üretiliyor...'):
            r = requests.post(url, headers=headers, json=payload)

        if r.status_code == 200:
            audio_bytes = r.content
            st.success('Ses başarıyla üretildi!')

            st.audio(audio_bytes, format='audio/mp3')

            st.download_button(
                label='⬇️ MP3 İndir',
                data=BytesIO(audio_bytes),
                file_name='niko_voice.mp3',
                mime='audio/mpeg',
                use_container_width=True
            )

            st.markdown('---')
            st.subheader('🎥 Video Önizleme')
            st.write(f'**Format:** {fmt}')
            st.write(f'**Aynalama:** {'Açık' if mirror else 'Kapalı'}')
            st.write(f'**Glow:** {'Açık' if glow else 'Kapalı'}')

            if fmt.startswith('Shorts'):
                st.image('https://placehold.co/540x960/111827/FFFFFF?text=Shorts+Preview')
            else:
                st.image('https://placehold.co/1280x720/111827/FFFFFF?text=Long+Preview')

            st.info('Bu ilk sürüm ses üretir. Sonraki adımda gerçek MP4 video üretimi ekleyeceğiz.')
        else:
            st.error(f'Hata: {r.status_code}')
            try:
                st.code(r.text)
            except:
                pass
