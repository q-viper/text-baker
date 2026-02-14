import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import shutil
import re
import hashlib

def process_chunk(chunk_args):
    """Process batch of files"""
    dest_root = chunk_args[0]
    source_root = chunk_args[1]
    copied = 0
    for src_path in chunk_args[2]:
        src = Path(src_path)
        try:
            if src.exists():
                # Preserve folder structure relative to source root
                rel_dir = src.parent.relative_to(source_root)
                
                # Clean filename: keep alphanumeric chars, replace special chars with underscore
                clean_name = re.sub(r'[^a-zA-Z0-9]', '_', src.stem)
                # Remove consecutive underscores and strip leading/trailing underscores
                clean_name = re.sub(r'_+', '_', clean_name).strip('_')
                # Ensure we have a valid filename (fallback if all chars were special)
                if not clean_name:
                    clean_name = 'file'
                
                # Add hash of original filename to ensure uniqueness
                name_hash = hashlib.md5(src.name.encode('utf-8')).hexdigest()[:8]
                unique_name = f"{clean_name}_{name_hash}"
                
                dest_file = Path(dest_root) / rel_dir / f"{unique_name}{src.suffix}"
                dest_file.parent.mkdir(exist_ok=True, parents=True)
                
                # Only copy if destination doesn't exist or is different
                if not dest_file.exists():
                    shutil.copy2(src, dest_file)
                    copied += 1
        except Exception as e:
            print(f"Error copying {src}: {e}")
    return copied

if __name__ == "__main__":
    root = r'F:\work\dataset\handwritten_ds'
    dest_root = r'C:\Users\Viper\Desktop\text_baker\assets'
    
    source_root = Path(root)
    print(f"Scanning files in {root}...")
    # Exclude _MACOSX folders
    all_pngs = [p for p in source_root.rglob('*.png') if 'MACOSX' not in str(p)]
    print(f"Using {mp.cpu_count()} cores for {len(all_pngs):,} files")
    
    # Split into chunks for each core
    cores = mp.cpu_count()
    chunk_size = len(all_pngs) // cores + 1
    # Pass source_root to each chunk for proper relative path calculation
    chunks = [(dest_root, root, all_pngs[i:i+chunk_size]) for i in range(0, len(all_pngs), chunk_size)]
    
    total_copied = 0
    with ProcessPoolExecutor(max_workers=cores) as executor:
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]
        for future in futures:
            total_copied += future.result()
            print(f"Copied: {total_copied}")
    
    print(f"✅ {total_copied} files copied with {cores} cores!")
