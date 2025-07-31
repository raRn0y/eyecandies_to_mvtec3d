# eyecandies_to_mvtec3d
Modify the folder format of Eyecandies dataset to be consistent with that of Mvtec3d AD dataset.

1. **Directory Structure Processing**:
   - Organizes files from a source directory into a standardized target directory structure
   - Handles three dataset splits: `train`, `test_public`, and `val`

2. **File Classification**:
   - Identifies three file types:
     - RGB images (`*_image_5.png`)
     - Depth maps (`*_depth.png`)
     - Mask files (`*_mask.png`)
   - Uses regex patterns for strict filename matching

3. **Quality Classification**:
   - For test files, reads YAML metadata to classify as 'good' or 'bad' quality
   - Uses the 'anomalous' flag in metadata (1 = bad, 0 = good)

4. **Target Structure**:
   ```
   target_dir/
   └── category/
       ├── train/
       │   └── good/
       │       ├── rgb/        # For RGB images
       │       ├── xyz/        # For depth maps
       │       └── gt/         # For mask files
       ├── test_public/
       │   ├── good/           # Normal samples
       │   └── bad/            # Anomalous samples
       └── val/
           └── good/
   ```

5. **File Renumbering**:
   - Renames all files to maintain consistent 4-digit numbering (0000.png, 0001.png, etc.)
   - Preserves original ordering while simplifying filenames

## Key Components

- **process_directory()**: Main driver that processes each category folder
- **process_split_dir()**: Handles files within each dataset split
- **renumber_files()**: Standardizes file numbering across the dataset
- **Error Handling**: Checks for required dependencies (PyYAML and tqdm)

## Usage

1. Specify source and target directories
2. The script will:
   - Clear any existing target directory
   - Process all files from source to target
   - Renumber files sequentially
   - Maintain the original directory structure while adding quality subfolders for test data
