import streamlit as st
from datetime import datetime
from PIL import Image

from core.config import BIN_MAP
from core.inference import run_model
from core.gemini_client import get_disposal_tips
from core.hardware import actuate_sort
from utils.storage import append_scan, load_scans


# ---------- Page setup ----------
st.set_page_config(
    page_title="E-Wizard",
    page_icon="🪄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🪄 E-Wizard")
st.caption("AI-powered e-waste identification + sorting for UGA. Scan items, sort safely, and learn proper disposal.")


# ---------- Sidebar ----------
st.sidebar.header("Controls")

mode = st.sidebar.radio(
    "Input mode",
    ["Upload Image", "Use Camera"],
    index=0,
)

use_gemini = st.sidebar.toggle("Gemini disposal tips", value=False)
use_servo = st.sidebar.toggle("Actuate sorter (servo)", value=False)

st.sidebar.divider()
st.sidebar.markdown("### Categories")
st.sidebar.write(", ".join(BIN_MAP.keys()))
st.sidebar.caption("Tip: Start with Upload mode to move fast.")


# ---------- Layout ----------
left, right = st.columns([1.1, 0.9], gap="large")

with left:
    st.subheader("1) Capture or Upload")

    image: Image.Image | None = None

    if mode == "Use Camera":
        cam = st.camera_input("Take a photo of the item")
        if cam is not None:
            image = Image.open(cam).convert("RGB")
    else:
        up = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if up is not None:
            image = Image.open(up).convert("RGB")

    if image is not None:
        st.image(image, use_container_width=True)
    else:
        st.info("Provide an image to scan an item.")


with right:
    st.subheader("2) Scan + Sort")

    scan_btn = st.button(
        "🔍 Scan Item",
        type="primary",
        use_container_width=True,
        disabled=(image is None),
    )

    if scan_btn:
        with st.spinner("Running model inference..."):
            label, confidence = run_model(image)

        bin_name = BIN_MAP.get(label, BIN_MAP["unknown"])

        tips = None
        if use_gemini:
            with st.spinner("Asking Gemini for disposal guidance..."):
                tips = get_disposal_tips(label)

        if use_servo:
            with st.spinner("Actuating sorter..."):
                actuate_sort(bin_name)

        # log scan
        append_scan({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "label": label,
            "confidence": float(confidence),
            "bin": bin_name,
        })

        st.success("Scan complete!")
        c1, c2 = st.columns(2)
        c1.metric("Detected", label)
        c2.metric("Confidence", f"{confidence:.2f}")

        st.write("**Bin:**", bin_name)
        if tips:
            st.info(tips)


st.divider()


# ---------- History + Stats ----------
st.subheader("Recent Scans")

df = load_scans()
if len(df) == 0:
    st.caption("No scans yet.")
else:
    st.dataframe(df.sort_values("timestamp", ascending=False), use_container_width=True)

st.subheader("Stats")
if len(df) > 0:
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total", int(len(df)))
    s2.metric("Batteries", int((df["label"] == "battery").sum()))
    s3.metric("Devices", int((df["label"] == "device").sum()))
    s4.metric("Unknown", int((df["label"] == "unknown").sum()))