import streamlit as st
from datetime import datetime
from PIL import Image

from core.config import BIN_MAP, STATIC_TIPS
from core.inference import run_model
from core.gemini_client import get_disposal_tips
from core.hardware import actuate_sort
from utils.storage import append_scan, load_scans, clear_scans


# ---------------- Page setup ----------------
st.set_page_config(page_title="E-Wizard", page_icon="🪄", layout="wide")
st.title("🪄 E-Wizard")
st.caption("AI-powered e-waste identification + sorting for UGA. Scan items, sort safely, and get disposal guidance.")

# ---------------- Sidebar ----------------
st.sidebar.header("Controls")
input_mode = st.sidebar.radio("Input Mode", ["Upload", "Camera"], index=0)
use_gemini = st.sidebar.toggle("Enable Gemini guidance", value=True)
use_servo = st.sidebar.toggle("Enable servo sorting", value=False)
dev_mode = st.sidebar.toggle("Developer mode", value=False)
conf_thresh = st.sidebar.slider("Confidence threshold", 0.0, 1.0, 0.25, 0.05)


st.sidebar.divider()
if st.sidebar.button("🗑️ Clear scan history"):
    clear_scans()
    st.sidebar.success("History cleared!")
# ---------------- Session state ----------------
if "last_scan" not in st.session_state:
    st.session_state.last_scan = None
if "pending_override" not in st.session_state:
    st.session_state.pending_override = False

# ---------------- Load history ----------------
df = load_scans()

# ---------------- Hero stats ----------------
c1, c2, c3, c4 = st.columns(4)
total = int(len(df))
components = int(df["label"].isin(["cpu", "ram_stick"]).sum()) if total else 0
storage = int((df["label"] == "flash_drive").sum()) if total else 0
unk = int((df["label"] == "unknown").sum()) if total else 0

c1.metric("Total items", total)
c2.metric("Components (CPU/RAM)", components)
c3.metric("Storage (Flash drives)", storage)
c4.metric("Unknown", unk)

st.divider()

# ---------------- Main layout ----------------
left, right = st.columns([1.05, 0.95], gap="large")

with left:
    st.subheader("Input")
    image = None

    if input_mode == "Camera":
        cam = st.camera_input("Take a photo")
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

    scan = st.button("🔍 Scan Item", type="primary", use_container_width=True, disabled=(image is None))

with right:
    st.subheader("Results") 
    if (not scan) and st.session_state.last_scan:
        last = st.session_state.last_scan
        st.info(f"Last scan: **{last['label']}** → **{last['bin']}** (conf {last['confidence']:.2f})")


    if scan and image is not None:
        with st.spinner("Running detection..."):
            # run_model returns (label, conf, annotated_img_or_None, raw_optional)
            label, conf, annotated, raw = run_model(image)
            st.session_state.pending_override = True

        low_conf = conf < conf_thresh
        if low_conf:
            label = "unknown"
            st.warning("Low confidence — sending to Manual Review. You can override below.")
        else:
            st.session_state.pending_override = False

        bin_name = BIN_MAP.get(label, BIN_MAP["unknown"])

        was_overridden = False

        # Manual override (demo safety)
        override_label = None
        if st.session_state.pending_override and label == "unknown":
            st.subheader("Manual override")
            cA, cB, cC = st.columns(3)
            if cA.button("Mark as CPU"):
                override_label = "cpu"
            if cB.button("Mark as RAM"):
                override_label = "ram_stick"
            if cC.button("Mark as Flash Drive"):
                override_label = "flash_drive"

            if override_label is not None:
                label = override_label
                bin_name = BIN_MAP.get(label, BIN_MAP["unknown"])
                was_overridden = True
                st.success(f"Override applied: {label} → {bin_name}")
                st.session_state.pending_override = False

        # Gemini or fallback
        tips = None

        st.session_state.last_scan = {
        "label": label,
        "confidence": conf,
        "bin": bin_name,
        "tips": tips,  # this will be filled after Gemini runs
        "raw": raw, 
        "low_conf": low_conf,
        }
        
        if use_gemini:
            try:
                with st.spinner("Generating disposal guidance..."):
                    tips = get_disposal_tips(label)
            except Exception as e:
                tips = f"Gemini error: {e}"

        if tips is None:
            tips = STATIC_TIPS.get(label, STATIC_TIPS["unknown"])

        st.session_state.last_scan["tips"] = tips
        st.session_state.last_scan["label"] = label
        st.session_state.last_scan["bin"] = bin_name


        # Servo actuation (optional)
        if use_servo and (not low_conf):
            with st.spinner("Sorting item..."):
                actuate_sort(bin_name)

        # Log scan
        append_scan({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "label": label,
            "confidence": float(conf),
            "bin": bin_name,
            "overridden": was_overridden,
        })

        # Display results
        st.success("Scan complete!")
        m1, m2 = st.columns(2)
        m1.metric("Detected", label)
        m2.metric("Confidence", f"{conf:.2f}")
        st.write("**Bin:**", bin_name)
        if was_overridden:
            st.caption("Label was manually overridden by user")

        if raw and "top" in raw and raw["top"]["class_name"] is not None:
            st.caption(
                f"Top YOLO: {raw['top']['class_name']} "
                f"({raw['top']['confidence']:.2f}) → {raw['top']['mapped_label']}"
            )

        if annotated is not None:
            st.image(annotated, caption="YOLO annotated output", use_container_width=True)

        st.subheader("♻️ Disposal Guidance")

        def render_guidance(md: str):
            parts = md.split("## ")
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                title, *rest = part.split("\n", 1)
                body = rest[0].strip() if rest else ""
                with st.container(border=True):
                    st.markdown(f"### {title.strip()}")
                    st.markdown(body)

        render_guidance(tips)


        if dev_mode and raw is not None:
            st.subheader("Raw detections (dev)")
            st.write(raw)

    else:
        st.caption("Results will appear here after you scan an item.")

st.divider()

st.subheader("Recent scans")
df = load_scans()
if len(df) == 0:
    st.caption("No scans yet.")
else:
    st.dataframe(df.sort_values("timestamp", ascending=False).head(25), use_container_width=True)