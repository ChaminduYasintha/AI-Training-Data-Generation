import streamlit as st
import asyncio
import pandas as pd
import json
import os

from ingestion.unified_loader import UnifiedLoader
from processing.text_kitchen import TextKitchen
from processing.smart_chunker import SmartChunker
from generation.job_assignment_office import JobAssignmentOffice
from quality.evaluator_station import EvaluatorStation
from export.master_packager import MasterPackager

# --- App Configuration ---
st.set_page_config(page_title="Stratova Data Factory", layout="wide", page_icon="🏭")
st.title("AI Training Data Generation Factory")
st.markdown("Enterprise pipeline to automatically ingest, process, generate, evaluate, and package training datasets for LLMs.")

# Setup Session State
if "raw_data" not in st.session_state: st.session_state.raw_data = []
if "chunks" not in st.session_state: st.session_state.chunks = []
if "generated_dataset" not in st.session_state: st.session_state.generated_dataset = []
if "approved_dataset" not in st.session_state: st.session_state.approved_dataset = []

# --- Custom Styling ---
st.markdown('''
<style>
.stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
''', unsafe_allow_html=True)

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📂 1. Ingestion", 
    "✂️ 2. Processing", 
    "🧠 3. Generation", 
    "⚖️ 4. Evaluator", 
    "📦 5. Export"
])

# 1. Ingestion Tab
with tab1:
    st.header("Unified Ingestion Center")
    
    urls_input = st.text_area("Enter bulk URLs (one per line):", placeholder="https://en.wikipedia.org/wiki/Artificial_intelligence\nhttps://en.wikipedia.org/wiki/Machine_learning")
    uploaded_files = st.file_uploader("Upload Documents (PDF, TXT)", type=["pdf", "txt"], accept_multiple_files=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Ingest Data"):
            if urls_input.strip() or uploaded_files:
                try:
                    with st.spinner("Ingesting from sources..."):
                        loader = UnifiedLoader()
                        all_loaded_data = []
                        
                        # Process URLs
                        if urls_input.strip():
                            urls = [u.strip() for u in urls_input.split('\n') if u.strip()]
                            for url in urls:
                                all_loaded_data.extend(loader.load_resource(url))
                                
                        # Process Uploaded Files
                        if uploaded_files:
                            os.makedirs("temp_uploads", exist_ok=True)
                            for uploaded_file in uploaded_files:
                                temp_path = os.path.join("temp_uploads", uploaded_file.name)
                                with open(temp_path, "wb") as f:
                                    f.write(uploaded_file.getbuffer())
                                all_loaded_data.extend(loader.load_resource(temp_path))
                        
                        st.session_state.raw_data = all_loaded_data
                    st.success(f"Ingested {len(st.session_state.raw_data)} documents.")
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")
            else:
                st.warning("Please provide URLs or upload files.")
    with col2:
        if st.session_state.raw_data:
            st.text_area("Preview (First Document):", st.session_state.raw_data[0]['text'][:1000] + "...", height=200)

# 2. Processing Tab
with tab2:
    st.header("Text Kitchen & Smart Chunker")
    col1, col2 = st.columns(2)
    with col1:
        chunk_size = st.number_input("Chunk Size (words)", min_value=50, value=1000, step=50)
    with col2:
        overlap = st.number_input("Overlap (words)", min_value=0, value=200, step=10)

    if st.button("Process & Chunk"):
        if st.session_state.raw_data:
            with st.spinner("Cleaning and Chunking..."):
                kitchen = TextKitchen()
                chunker = SmartChunker(chunk_size=chunk_size, overlap=overlap)
                all_chunks = []
                for doc in st.session_state.raw_data:
                    clean_text = kitchen.clean(doc['text'])
                    all_chunks.extend(chunker.chunk_text(clean_text))
                st.session_state.chunks = all_chunks
            st.success(f"Generated {len(st.session_state.chunks)} semantic chunks.")
            if st.session_state.chunks:
                st.info(f"Sample Chunk: {st.session_state.chunks[0][:500]}...")
        else:
            st.warning("Please ingest data first.")

# 3. Generation Tab
with tab3:
    st.header("Job Assignment Office (Async Generation)")
    st.markdown("Uses an active LLM connection (or Simulation Mode) to concurrently generate examples from chunks.")
    
    col1, col2 = st.columns(2)
    with col1:
        task_types = st.multiselect("Select Task Templates (Multiple Allowed):", ["qa", "summary", "classification"], default=["qa"], format_func=lambda x: {"qa": "Q&A Generation", "summary": "Summarization", "classification": "Data Classification"}[x])
    with col2:
        provider = st.selectbox("Select AI Provider:", ["openai", "anthropic", "gemini"], format_func=lambda x: x.capitalize())
    
    if st.button("Start Massive Generation"):
        if not task_types:
            st.error("Please select at least one task template.")
        elif st.session_state.chunks:
            with st.spinner(f"Concurrent generation using {provider.capitalize()} across {len(task_types)} task(s) in progress..."):
                office = JobAssignmentOffice()
                
                async def run_all_tasks():
                    all_results = []
                    tasks = [office.generate_dataset(st.session_state.chunks, t_type, provider=provider) for t_type in task_types]
                    type_results = await asyncio.gather(*tasks)
                    for res in type_results:
                        all_results.extend(res)
                    return all_results
                
                st.session_state.generated_dataset = asyncio.run(run_all_tasks())
            st.success(f"Generated {len(st.session_state.generated_dataset)} examples combined.")
            
            # Analytics & Cost Monitor
            if st.session_state.generated_dataset:
                total_prompt = sum(ex.get("usage", {}).get("prompt", 0) for ex in st.session_state.generated_dataset)
                total_completion = sum(ex.get("usage", {}).get("completion", 0) for ex in st.session_state.generated_dataset)
                
                # Estimated Pricing logic (Using Gemini 1.5 Flash rough defaults)
                # Flash: ~$0.075 / 1M input tokens, ~$0.30 / 1M output tokens (approx estimates)
                cost = (total_prompt / 1_000_000 * 0.075) + (total_completion / 1_000_000 * 0.3)
                
                st.markdown(" Live Token & Cost Monitor")
                m1, m2, m3 = st.columns(3)
                m1.metric("Input Tokens", f"{total_prompt:,}")
                m2.metric("Output Tokens", f"{total_completion:,}")
                m3.metric("Estimated Cost", f"${cost:.5f}")
                
                st.json(st.session_state.generated_dataset[:2]) # Preview
        else:
            st.warning("Please process chunks first.")

# 4. Evaluator Tab
with tab4:
    st.header("Evaluator Station (Quality Control)")
    if st.button("Run Strict Evaluation"):
        if st.session_state.generated_dataset:
            with st.spinner("Filtering against toxicity, coherence, and relevance checks..."):
                station = EvaluatorStation()
                st.session_state.approved_dataset = station.filter_dataset(st.session_state.generated_dataset)
                rejected = len(st.session_state.generated_dataset) - len(st.session_state.approved_dataset)
            st.success(f"Evaluation Complete. Approved: {len(st.session_state.approved_dataset)} | Rejected: {rejected}")
            if st.session_state.approved_dataset:
                st.dataframe(pd.DataFrame(st.session_state.approved_dataset).head(10))
        else:
            st.warning("Generate a dataset first.")

# 5. Export Tab
with tab5:
    st.header("Master Packager")
    export_format = st.radio("Export Format:", ["CSV", "JSONL"])
    file_name = st.text_input("Output File Name:", "final_dataset." + export_format.lower())

    if st.button("Package & Export"):
        if st.session_state.approved_dataset:
            packager = MasterPackager()
            filepath = os.path.join(os.getcwd(), file_name)
            try:
                if export_format == "CSV":
                    packager.export_to_csv(st.session_state.approved_dataset, filepath)
                else:
                    packager.export_to_jsonl(st.session_state.approved_dataset, filepath)
                st.success(f"Successfully exported to **{filepath}**!")
            except Exception as e:
                st.error(f"Export failed: {e}")
        else:
            st.warning("No approved dataset to export. Verify through the evaluator station.")
