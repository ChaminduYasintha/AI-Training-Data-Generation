import asyncio
import argparse
from ingestion.unified_loader import UnifiedLoader
from processing.text_kitchen import TextKitchen
from processing.smart_chunker import SmartChunker
from generation.job_assignment_office import JobAssignmentOffice
from quality.evaluator_station import EvaluatorStation
from export.master_packager import MasterPackager

async def main():
    parser = argparse.ArgumentParser(description="AI Training Data Generation Factory CLI")
    parser.add_argument("--source", type=str, required=True, help="URL or file path to ingest")
    parser.add_argument("--task", type=str, choices=["qa", "summary", "classification"], required=True, help="Task type to generate")
    parser.add_argument("--output", type=str, default="dataset.csv", help="Output CSV file path")
    args = parser.parse_args()

    print(f"[*] Starting Pipeline for source: {args.source}")
    
    # 1. Ingest
    print("[*] Ingesting data...")
    loader = UnifiedLoader()
    raw_data = loader.load_resource(args.source)
    
    # 2. Process
    print("[*] Processing text...")
    kitchen = TextKitchen()
    chunker = SmartChunker(chunk_size=500, overlap=100) # smaller for demo
    
    all_chunks = []
    for doc in raw_data:
        clean_text = kitchen.clean(doc['text'])
        chunks = chunker.chunk_text(clean_text)
        all_chunks.extend(chunks)
    
    print(f"[*] Generated {len(all_chunks)} semantic chunks.")
    
    # 3. Generate
    print(f"[*] Generating {args.task} dataset using AI (asyncio)...")
    office = JobAssignmentOffice()
    dataset = await office.generate_dataset(all_chunks, args.task)
    
    # 4. Quality Control
    print("[*] Evaluating generated examples...")
    station = EvaluatorStation()
    approved_dataset = station.filter_dataset(dataset)
    print(f"[*] Approved {len(approved_dataset)} out of {len(dataset)} examples.")
    
    # 5. Export
    if approved_dataset:
        print(f"[*] Exporting to {args.output}...")
        packager = MasterPackager()
        packager.export_to_csv(approved_dataset, args.output)
    else:
        print("[-] No approved examples to export.")
        
    print("[*] Pipeline Complete.")

if __name__ == "__main__":
    asyncio.run(main())
