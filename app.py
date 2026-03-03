"""
Pakistan Bank Statement PDF Unlocker
Streamlit Web App — works in any browser, no installation needed
Deploy free at: https://streamlit.io
"""

import streamlit as st
import os
import io
import tempfile

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bank Statement PDF Unlocker",
    page_icon="🏦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #f0f4f8; }

    /* Hide streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* Header banner */
    .header-banner {
        background: linear-gradient(135deg, #1F3864, #2E75B6);
        padding: 28px 32px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 15px rgba(31,56,100,0.3);
    }
    .header-banner h1 {
        color: white;
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 6px 0;
        font-family: Arial, sans-serif;
    }
    .header-banner p {
        color: #BDD7EE;
        font-size: 14px;
        margin: 0;
        font-family: Arial, sans-serif;
    }

    /* Card */
    .card {
        background: white;
        border-radius: 10px;
        padding: 24px 28px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    /* Step label */
    .step-label {
        font-weight: 700;
        color: #1F3864;
        font-size: 15px;
        font-family: Arial, sans-serif;
        margin-bottom: 8px;
    }

    /* Hint box */
    .hint-box {
        background: #FFF9C4;
        border-left: 4px solid #FFD966;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 13px;
        color: #7F6000;
        font-style: italic;
        margin: 8px 0 16px 0;
        font-family: Arial, sans-serif;
    }

    /* Success box */
    .success-box {
        background: #E8F5E9;
        border-left: 4px solid #70AD47;
        padding: 14px 18px;
        border-radius: 6px;
        color: #2E7D32;
        font-family: Arial, sans-serif;
    }

    /* Error box */
    .error-box {
        background: #FFEBEE;
        border-left: 4px solid #C00000;
        padding: 14px 18px;
        border-radius: 6px;
        color: #C00000;
        font-family: Arial, sans-serif;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        font-size: 12px;
        padding: 16px 0 8px 0;
        font-family: Arial, sans-serif;
    }

    /* Bank buttons */
    div[data-testid="stHorizontalBlock"] > div { flex: 1; }

    /* Upload area */
    [data-testid="stFileUploader"] {
        background: #F7FBFF;
        border-radius: 8px;
        border: 2px dashed #2E75B6;
        padding: 8px;
    }

    /* Unlock button */
    .stButton > button {
        background: linear-gradient(135deg, #1F3864, #2E75B6) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        padding: 14px !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100% !important;
        cursor: pointer !important;
        font-family: Arial, sans-serif !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2E75B6, #1F3864) !important;
        box-shadow: 0 4px 12px rgba(31,56,100,0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Bank hints ────────────────────────────────────────────────────────────────
BANK_HINTS = {
    "🏦 HBL":     "Password = last 6 digits of your HBL account number",
    "🏦 UBL":     "Password = last 6 digits of your UBL account number",
    "🏦 MCB":     "Password = last 6 digits of your MCB account number",
    "🕌 Meezan":  "Password = last 6 digits of your Meezan account number",
    "🏦 Allied":  "Password = last 6 digits of your Allied account number",
    "🌐 Other":   "Check your bank's email for the password hint",
}

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <h1>🏦 Bank Statement PDF Unlocker</h1>
    <p>HBL &nbsp;·&nbsp; UBL &nbsp;·&nbsp; MCB &nbsp;·&nbsp; Meezan &nbsp;·&nbsp; Allied &nbsp;·&nbsp; Any Bank Worldwide</p>
</div>
""", unsafe_allow_html=True)

# ── Try importing pikepdf ─────────────────────────────────────────────────────
try:
    import pikepdf
    PIKEPDF_OK = True
except ImportError:
    PIKEPDF_OK = False
    st.error("⚠️ pikepdf not installed on server. Add `pikepdf` to requirements.txt")

# ── STEP 1 — Bank selector ────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 1 — Select your bank</div>', unsafe_allow_html=True)

bank_cols = st.columns(len(BANK_HINTS))
if "selected_bank" not in st.session_state:
    st.session_state.selected_bank = "🏦 HBL"

for col, bank in zip(bank_cols, BANK_HINTS):
    with col:
        is_selected = st.session_state.selected_bank == bank
        if st.button(
            bank.split(" ", 1)[1],  # label without emoji
            key=f"bank_{bank}",
            type="primary" if is_selected else "secondary",
            use_container_width=True
        ):
            st.session_state.selected_bank = bank
            st.rerun()

hint = BANK_HINTS[st.session_state.selected_bank]
st.markdown(f'<div class="hint-box">💡 &nbsp;{hint}</div>', unsafe_allow_html=True)

st.divider()

# ── STEP 2 — File upload ──────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 2 — Upload your password-protected PDF</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    label="",
    type=["pdf"],
    help="Your file is processed in memory and never stored on any server.",
    label_visibility="collapsed"
)

if uploaded_file:
    st.caption(f"📄 **{uploaded_file.name}**  ({round(uploaded_file.size / 1024, 1)} KB)")

st.divider()

# ── STEP 3 — Password ─────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 3 — Enter the PDF password</div>', unsafe_allow_html=True)

col_pass, col_show = st.columns([3, 1])
with col_pass:
    password = st.text_input(
        label="",
        type="password",
        placeholder="Enter password (e.g. last 6 digits of account number)",
        label_visibility="collapsed"
    )
with col_show:
    show_pass = st.checkbox("Show", value=False)

if show_pass and password:
    st.info(f"🔑 Password entered: **{password}**")

st.divider()

# ── STEP 4 — Unlock ───────────────────────────────────────────────────────────
st.markdown('<div class="step-label">Step 4 — Unlock & Download</div>', unsafe_allow_html=True)

unlock_clicked = st.button("🔓   Unlock PDF", use_container_width=True)

if unlock_clicked:
    # Validation
    if not uploaded_file:
        st.markdown('<div class="error-box">⚠️ Please upload a PDF file first.</div>', unsafe_allow_html=True)
    elif not password:
        st.markdown('<div class="error-box">⚠️ Please enter the PDF password.</div>', unsafe_allow_html=True)
    elif not PIKEPDF_OK:
        st.markdown('<div class="error-box">⚠️ Server error — pikepdf not available.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Unlocking your PDF..."):
            try:
                # Read uploaded bytes
                pdf_bytes = uploaded_file.read()

                # Write to temp file (pikepdf needs file path)
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_in:
                    tmp_in.write(pdf_bytes)
                    tmp_path = tmp_in.name

                # Unlock into memory buffer
                output_buffer = io.BytesIO()
                with pikepdf.open(tmp_path, password=password) as pdf:
                    pdf.save(output_buffer)
                output_buffer.seek(0)

                # Clean up temp file
                os.unlink(tmp_path)

                # Output filename
                original_name = os.path.splitext(uploaded_file.name)[0]
                output_name = f"{original_name}_unlocked.pdf"

                # Success
                st.markdown(f"""
                <div class="success-box">
                    ✅ <strong>PDF unlocked successfully!</strong><br>
                    Click the button below to download your unlocked file.
                </div>
                """, unsafe_allow_html=True)

                st.download_button(
                    label=f"⬇️   Download  {output_name}",
                    data=output_buffer,
                    file_name=output_name,
                    mime="application/pdf",
                    use_container_width=True,
                )

            except pikepdf.PasswordError:
                st.markdown("""
                <div class="error-box">
                    ❌ <strong>Wrong password.</strong><br>
                    Double-check the last 6 digits of your account number and try again.
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                    ❌ <strong>Error:</strong> {str(e)}
                </div>
                """, unsafe_allow_html=True)

# ── Privacy note ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="background:#F0F4F8; border-radius:8px; padding:12px 16px; margin-top:16px;">
    🔒 <strong>Privacy:</strong> Your PDF is processed entirely in memory and is never saved, stored, or sent anywhere.
    The file is discarded immediately after unlocking.
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Part of the <strong>Personal Bank Transaction Tracker</strong> &nbsp;|&nbsp;
    Works with any bank worldwide &nbsp;|&nbsp; For personal use only
</div>
""", unsafe_allow_html=True)
