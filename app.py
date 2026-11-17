import os
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types
from matcher import ask_gemini, decide
from recommend import names, suggest, bundles, offer, top_sellers

st.set_page_config(page_title="RetailDeep", layout="centered")
st.title("🛒 RetailDeep Assistant")

key = os.environ.get('GEMINI_API_KEY', '')
if not key:
    try:
        key = st.secrets['GEMINI_API_KEY']
    except Exception:
        key = ''
if not key and os.path.exists('gemini_key.txt'):
    key = open('gemini_key.txt', encoding='utf-8-sig').read().strip()
if not key:
    st.error('حط الـ API key في Secrets أو متغير GEMINI_API_KEY أو ملف gemini_key.txt')
    st.stop()


@st.cache_resource
def get_client(k):
    return genai.Client(api_key=k, http_options=types.HttpOptions(timeout=30000))


client = get_client(key)

tab1, tab2 = st.tabs(["📷 الكاميرا", "📁 رفع صورة"])
with tab1:
    cam_img = st.camera_input("صور المنتج")
with tab2:
    up_img = st.file_uploader("ارفع صورة المنتج", type=["jpg", "jpeg", "png", "webp"])

img_file = cam_img if cam_img is not None else up_img

if img_file is not None:
    image = Image.open(img_file).convert('RGB')
    with st.spinner("جاري التعرف على المنتج..."):
        try:
            r = ask_gemini(client, image)
        except Exception as e:
            st.error(f"مشكلة في الاتصال بـ Gemini: {e}")
            st.stop()
    status, shown, pid = decide(image, r)
    st.image(shown, caption="المنتج")
    if status == 'none':
        st.warning("مفيش منتج في الصورة")
    elif status == 'nomatch':
        st.error("مفيش منتج قريب من ده في الداتا بتاعتنا")
    elif status == 'unsure':
        st.warning("مش متأكد من المنتج، صوره تاني من قرب وإضاءة أحسن")
    else:
        st.success(f"أقرب منتج في الداتا: {names[pid]}")
        if status == 'similar':
            st.caption("تطابق تقريبي: نفس نوع المنتج لكن الماركة أو الحجم ممكن يختلف")

        st.subheader("🛍️ ممكن تشتري معاه")
        sug = suggest(pid)
        if sug:
            for s in sug:
                st.write('- ' + s)
        else:
            st.write('مفيش منتج بيتشرى معاه بشكل واضح في الداتا')
            st.caption('الأكتر مبيعاً عموماً (مش مرتبط بالمنتج ده): ' + '، '.join(top_sellers))

        st.subheader("🎁 الباندلات")
        bnd = bundles(pid)
        if bnd:
            for b in bnd:
                st.info(b)
        else:
            st.write('مفيش باندل واضح للمنتج ده')

        st.subheader("🏷️ العروض")
        st.write(offer(pid))
