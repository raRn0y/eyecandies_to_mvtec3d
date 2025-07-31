import os
import shutil
import yaml
from tqdm import tqdm

def process_directory(source_dir, target_dir):
    """Process each category folder in the source directory"""
    categories = [d for d in os.listdir(source_dir) 
                 if os.path.isdir(os.path.join(source_dir, d))]
    
    for category in tqdm(categories, desc="Processing categories"):
        print('Processing:', category)
        category_path = os.path.join(source_dir, category)
        
        for split_type in ['train', 'test_public', 'val']:
            split_path = os.path.join(category_path, split_type, 'data')
            if not os.path.exists(split_path):
                print('Path does not exist')
                continue
                
            process_split_dir(split_path, split_type, target_dir, category)

def process_split_dir(split_path, split_type, target_dir, category):
    """Process files in train/test/val directories"""
    files = [f for f in os.listdir(split_path) 
             if os.path.isfile(os.path.join(split_path, f)) and 
             not f.endswith('.yaml')]  # Exclude metadata files
    
    # Use regex for strict filename pattern matching
    import re
    image_pattern = re.compile(r'^\d+_image_5\.png$')
    depth_pattern = re.compile(r'^\d+_depth\.png$')
    mask_pattern = re.compile(r'^\d+_mask\.png$')
    
    for filename in tqdm(files, desc=f"{category}/{split_type}", leave=False):
        # Extract numeric prefix
        if image_pattern.match(filename):
            prefix = filename.split('_')[0]
            file_type = 'image'
        elif depth_pattern.match(filename):
            prefix = filename.split('_')[0]
            file_type = 'depth'
        elif mask_pattern.match(filename):
            prefix = filename.split('_')[0]
            file_type = 'mask'
        else:
            continue  # Skip files that don't match the pattern
            
        # Process test metadata
        if split_type == 'test_public':
            metadata_file = f"{prefix}_metadata.yaml"
            metadata_path = os.path.join(split_path, metadata_file)
            quality = 'good'  # Default value
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = yaml.safe_load(f)
                    quality = 'bad' if metadata.get('anomalous', 0) == 1 else 'good'
                except:
                    pass
        else:
            quality = 'good'
        
        # Determine target subdirectory
        if file_type == 'image':
            dest_subdir = os.path.join(target_dir, category, split_type, quality, 'rgb')
        elif file_type == 'depth':
            dest_subdir = os.path.join(target_dir, category, split_type, quality, 'xyz')
        elif file_type == 'mask':
            dest_subdir = os.path.join(target_dir, category, split_type, quality, 'gt')
        else:
            continue
                
        os.makedirs(dest_subdir, exist_ok=True)
        shutil.copy2(os.path.join(split_path, filename), 
                    os.path.join(dest_subdir, filename))

def renumber_files(target_dir):
    """Renumber all files (starting from 0)"""
    print("\nRenumbering files...")
    for root, dirs, files in os.walk(target_dir):
        if not files:
            continue
            
        # Only process target files
        target_files = [f for f in files if any(f.endswith(ext) for ext in 
                      ['_image_5.png', '_depth.png', '_mask.png'])]
        if not target_files:
            continue
            
        # Group by original prefix
        file_groups = {}
        for f in target_files:
            prefix = f.split('_')[0]
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append(f)
        
        # Sort by original prefix and renumber
        sorted_prefixes = sorted(file_groups.keys(), key=lambda x: int(x))
        for new_num, old_prefix in enumerate(sorted_prefixes):
            for old_name in file_groups[old_prefix]:
                parts = old_name.split('_')
                new_name = f"{new_num:03d}.png"  # Maintain 4-digit numbering with leading zeros
                
                old_path = os.path.join(root, old_name)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)

def main():
    source_dir = '/home/wb/dataset-eyecandies'
    target_dir = '/home/wb/Eye/eyecandies'
    
    print("="*50)
    print("Dataset Processing Tool")
    print(f"Source Directory: {os.path.abspath(source_dir)}")
    print(f"Target Directory: {os.path.abspath(target_dir)}")
    print("="*50 + "\n")
    
    # Initialize target directory
    if os.path.exists(target_dir):
        print("Clearing existing target directory...")
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    
    # Process files
    process_directory(source_dir, target_dir)
    
    # Renumber files
    renumber_files(target_dir)
    
    print("\n" + "="*50)
    print("Processing complete! Results saved to:")
    print(os.path.abspath(target_dir))
    print("Directory structure example:")
    print("target/category/train/good/rgb/0000_image_5.png")
    print("target/category/test/bad/xyz/0001_depth.png")
    print("="*50)

if __name__ == "__main__":
    try:
        import yaml
        from tqdm import tqdm
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please run: pip install PyYAML tqdm")
        exit(1)
        
    main()
