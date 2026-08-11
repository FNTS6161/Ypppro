import streamlit as st
import requests
from io import BytesIO
from PIL import Image
from moviepy.editor import (
    AudioFileClip,
    ImageClip,
    TextClip,
    CompositeVideoClip
)
import tempfile
import os

st.set_page_config(page_title='NIKO VIDEO FACTORY', layout='centered')

st.title('🎬 NIKO VIDEO FACTORY')
st.caption('Gerçek MP4 video üretici')

script = st.text_area(
    'Senaryo',
    height=180,
    placeholder='Videoda okunacak metni yaz...'
)

api_key = st.text_input('ElevenLabs API Key', type='password')
voice_id = st.text_input('Voice ID')

fmt = st.radio(
    'Format',
    ['Shorts 9:16', 'Long 16:9'],
    horizontal=True
)

uploaded_bg = st.file_uploader(
    'Arka plan resmi yükle',
    type=['png', 'jpg', 'jpeg']
)

if st.button('🚀 MP4 Video Oluştur', use_container_width=True):

    if not script or not api_key or not voice_id:
        st.error('Lütfen senaryo, API key ve Voice ID gir.')
        st.stop()

    if uploaded_bg is None:
        st.error('Lütfen arka plan resmi yükle.')
        st.stop()

    with st.spinner('🎤 ElevenLabs sesi oluşturuluyor...'):

        url = f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}'

        headers = {
            'xi-api-key': api_key,
            'Content-Type': 'application/json'
        }

        payload = {
            'text': script,
            'model_id': 'eleven_multilingual_v2'
        }

        r = requests.post(url, headers=headers, json=payload)

    if r.status_code != 200:
        st.error(f'ElevenLabs hatası: {r.text}')
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:

        audio_path = os.path.join(tmpdir, 'voice.mp3')
        video_path = os.path.join(tmpdir, 'output.mp4')
        bg_path = os.path.join(tmpdir, 'bg.jpg')

        with open(audio_path, 'wb') as f:
            f.write(r.content)

        image = Image.open(uploaded_bg)
        image.save(bg_path)

        audio = AudioFileClip(audio_path)
        duration = audio.duration

        if fmt.startswith('Shorts'):
            W, H = 1080, 1920
        else:
            W, H = 1920, 1080

        bg_clip = (
            ImageClip(bg_path)
            .resize(height=H)
            .set_duration(duration)
        )

        bg_clip = bg_clip.resize(width=W)

        txt = (
            TextClip(
                script[:120],
                fontsize=64 if fmt.startswith('Shorts') else 48,
                color='white',
                method='caption',
                size=(W - 120, None),
                align='center'
            )
            .set_position(('center', H - 320))
            .set_duration(duration)
        )

        final = CompositeVideoClip([bg_clip, txt], size=(W, H))
        final = final.set_audio(audio)

        with st.spinner('🎬 MP4 oluşturuluyor...'):
            final.write_videofile(
                video_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )

        st.success('✅ Video hazır!')

        st.video(video_path)

        with open(video_path, 'rb') as f:
            st.download_button(
                '⬇️ MP4 İndir',
                data=f,
                file_name='niko_video.mp4',
                mime='video/mp4',
                use_container_width=True
            )
            