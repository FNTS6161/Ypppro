import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import AudioFileClip, ImageClip
import tempfile
import os

st.set_page_config(page_title='NIKO VIDEO FACTORY', layout='centered')

st.title('🎬 NIKO VIDEO FACTORY')
st.caption('ImageMagick gerektirmeyen çalışan sürüm')

script = st.text_area('Senaryo', height=180)
api_key = st.text_input('ElevenLabs API Key', type='password')
voice_id = st.text_input('Voice ID')

fmt = st.radio('Format', ['Shorts 9:16', 'Long 16:9'], horizontal=True)

uploaded_bg = st.file_uploader(
    'Arka plan resmi yükle',
    type=['png', 'jpg', 'jpeg']
)

if st.button('🚀 MP4 Video Oluştur'):

    if not script or not api_key or not voice_id or uploaded_bg is None:
        st.error('Tüm alanları doldur.')
        st.stop()

    # ElevenLabs ses üret
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

    if r.status_code != 200:
        st.error(r.text)
        st.stop()

    with tempfile.TemporaryDirectory() as tmp:

        audio_path = os.path.join(tmp, 'voice.mp3')
        image_path = os.path.join(tmp, 'bg.jpg')
        video_path = os.path.join(tmp, 'output.mp4')

        open(audio_path, 'wb').write(r.content)

        img = Image.open(uploaded_bg).convert('RGB')

        if fmt.startswith('Shorts'):
            W, H = 1080, 1920
        else:
            W, H = 1920, 1080

        img = img.resize((W, H))

        draw = ImageDraw.Draw(img)

        text = script[:140]

        try:
            font = ImageFont.truetype('DejaVuSans.ttf', 48)
        except:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        x = (W - tw) // 2
        y = H - th - 180

        draw.rounded_rectangle(
            [x - 30, y - 20, x + tw + 30, y + th + 20],
            radius=25,
            fill=(0, 0, 0)
        )

        draw.text((x, y), text, fill='white', font=font)

        img.save(image_path)

        audio = AudioFileClip(audio_path)

        clip = ImageClip(image_path).set_duration(audio.duration)
        clip = clip.set_audio(audio)

        with st.spinner('🎬 Video oluşturuluyor...'):
            clip.write_videofile(
                video_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )

        st.success('Video hazır!')

        st.video(video_path)

        st.download_button(
            '⬇️ MP4 İndir',
            open(video_path, 'rb'),
            file_name='niko_video.mp4',
            mime='video/mp4'
        )