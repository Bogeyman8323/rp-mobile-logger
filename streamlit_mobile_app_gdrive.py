# streamlit_mobile_app_gdrive.py
import io
from pathlib import Path
import streamlit as st
from openpyxl import load_workbook
from google_auth import build_auth_url, exchange_code_for_token, get_creds, sign_out
from gdrive_io import DriveClient, MIMETYPE_XLSX
from streamlit.components.v1 import declare_component

st.set_page_config(page_title="RP Logger (Mobile + Google Drive)", page_icon="📱", layout="centered")

st.title("📱 RP Set Logger — Mobile + Google Drive (drive.file + Picker)")

# Register local Picker component
picker_component_path = str((Path(__file__).parent / "picker_component").resolve())
drive_picker = declare_component("drive_picker", path=picker_component_path)

def pick_from_drive(oauth_token: str, api_key: str, app_id: str, multiselect: bool = False):
    """Render Picker and return list of fileIds selected by user."""
    file_ids = drive_picker(token=oauth_token, apiKey=api_key, appId=app_id, multiselect=str(multiselect))
    return file_ids or []

# --- Auth ---
with st.expander("Authentication", expanded=True):
    creds = get_creds() or exchange_code_for_token()
    if not creds:
        url = build_auth_url()
        st.markdown(f"[🔐 Sign in with Google]({url})")
        st.stop()
    else:
        st.success("Signed in with Google Drive")
        if st.button("Sign out"):
            sign_out()
            st.rerun()

client = DriveClient(get_creds())
api_key = st.secrets["google"]["api_key"]
app_id  = st.secrets["google"]["app_id"]
access_token = get_creds().token

st.header("Select your tracker (Google Picker)")
st.caption("Least‑privilege: scope is `drive.file`. Pick your .xlsx tracker to grant access only to that file.")

picked_ids = pick_from_drive(access_token, api_key, app_id, multiselect=False)
file_id = None
if picked_ids:
    file_id = picked_ids[0]
    st.success(f"Selected fileId: {file_id}")

st.divider()

if file_id and st.button("📥 Open from Drive"):
    try:
        content = client.download_file(file_id)
        st.session_state['wb_bytes'] = content
        st.session_state['current_file_id'] = file_id
        st.success("Workbook loaded. Log your sets below and save back to Drive.")
    except Exception as e:
        st.error(f"Download failed: {e}")

if 'wb_bytes' in st.session_state:
    wb_bytes = st.session_state['wb_bytes']
    wb = load_workbook(io.BytesIO(wb_bytes))

    DEFAULT_WEEKS = ["Week 1", "Week 2", "Week 3", "Week 4", "Deload"]
    DEFAULT_DAYS = ["Push A", "Pull A", "Legs A", "Push B", "Pull B", "Legs B"]

    weeks = [s for s in DEFAULT_WEEKS if s in wb.sheetnames] or [s for s in wb.sheetnames if s.lower().startswith("week") or s.lower()=="deload"]
    week = st.selectbox("Week", weeks, index=0)
    ws = wb[week]

    rows = list(ws.iter_rows(min_row=2, values_only=True))
    all_days = [r[0] for r in rows if r and r[0]]
    ordered_days = [d for d in DEFAULT_DAYS if d in all_days] + [d for d in all_days if d not in DEFAULT_DAYS]
    if not ordered_days:
        ordered_days = DEFAULT_DAYS

    if 'sel_day' not in st.session_state:
        st.session_state.sel_day = ordered_days[0]
    if 'ex_idx' not in st.session_state:
        st.session_state.ex_idx = 0

    sel_day = st.selectbox("Day", ordered_days, index=ordered_days.index(st.session_state.sel_day))
    st.session_state.sel_day = sel_day

    ex_list = [(i+2, r[1]) for i, r in enumerate(rows) if r and r[0]==sel_day and r[1]]
    ex_names = [ex for (_row, ex) in ex_list]

    if ex_names:
        st.write(f"**{sel_day}**: {', '.join(ex_names)}", unsafe_allow_html=True)
        st.session_state.ex_idx = st.number_input("Exercise #", min_value=0, max_value=max(0, len(ex_names)-1), value=st.session_state.ex_idx, step=1)
        row_idx, ex_name = ex_list[st.session_state.ex_idx]
    else:
        ex_name = st.text_input("Exercise (custom)")
        row_idx = None

    if ex_name:
        if row_idx:
            planned_sets = int(ws.cell(row=row_idx, column=4).value or 3)
            reps_target = ws.cell(row=row_idx, column=5).value or ""
            rir_target = ws.cell(row=row_idx, column=6).value or ""
            st.caption(f"Planned Sets: {planned_sets} · Reps: {reps_target} · RIR: {rir_target}")
        else:
            planned_sets = st.number_input("Planned Sets", 1, 5, value=3)

        weights, reps = [], []
        for i in range(1, 6):
            c1, c2 = st.columns(2)
            with c1:
                w = st.number_input(f"Set {i} — Weight", min_value=0.0, value=0.0, step=2.5, format="%.2f")
            with c2:
                r = st.number_input(f"Set {i} — Reps", min_value=0, value=0, step=1)
            weights.append(None if w==0 else w)
            reps.append(None if r==0 else r)

        colA, colB = st.columns(2)
        with colA:
            top_wt = st.number_input("Top Weight", min_value=0.0, value=0.0, step=2.5, format="%.2f")
        with colB:
            top_reps = st.number_input("Top Reps", min_value=0, value=0, step=1)
        if top_wt == 0: top_wt = None
        if top_reps == 0: top_reps = None

        def write_sets(target_row: int):
            for i in range(5):
                if weights[i] is not None:
                    ws.cell(row=target_row, column=7 + i*2).value = weights[i]
                if reps[i] is not None:
                    ws.cell(row=target_row, column=8 + i*2).value = reps[i]
            if top_wt is not None:
                ws.cell(row=target_row, column=17).value = top_wt
            if top_reps is not None:
                ws.cell(row=target_row, column=18).value = top_reps

        if st.button("Write sets to workbook"):
            if row_idx is None:
                new_row = ws.max_row + 1
                ws.cell(row=new_row, column=1).value = sel_day
                ws.cell(row=new_row, column=2).value = ex_name
                ws.cell(row=new_row, column=4).value = planned_sets
                ws.cell(row=new_row, column=19).value = f"=IFERROR(Q{new_row}*(1+R{new_row}/30),\"\")"
                ws.cell(row=new_row, column=20).value = f"=IFERROR(G{new_row}*H{new_row}+I{new_row}*J{new_row}+K{new_row}*L{new_row}+M{new_row}*N{new_row}+O{new_row}*P{new_row},\"\")"
                write_sets(new_row)
            else:
                write_sets(row_idx)
            out = io.BytesIO()
            wb.save(out)
            st.session_state['wb_bytes'] = out.getvalue()
            st.success("Sets written in memory. Use 'Save back to Drive' to upload.")

        st.divider()
        if st.button("☁️ Save back to Drive"):
            try:
                updated = client.update_file_content(st.session_state['current_file_id'], st.session_state['wb_bytes'], MIMETYPE_XLSX)
                st.success("Uploaded successfully to Google Drive.")
            except Exception as e:
                st.error(f"Upload failed: {e}")
else:
    st.info("Pick your tracker with the Google Picker to start logging.")
