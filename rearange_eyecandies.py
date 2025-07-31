import os
import shutil
import yaml
from tqdm import tqdm

def process_directory(source_dir, target_dir):
    """处理source目录下的每个类别文件夹"""
    categories = [d for d in os.listdir(source_dir) 
                 if os.path.isdir(os.path.join(source_dir, d))]
    
    for category in tqdm(categories, desc="处理类别"):
        print('processing:', category)
        category_path = os.path.join(source_dir, category)
        
        for split_type in ['train', 'test_public', 'val']:
            split_path = os.path.join(category_path, split_type, 'data')
            if not os.path.exists(split_path):
                print('path not exists')
                continue
                
            process_split_dir(split_path, split_type, target_dir, category)

def process_split_dir(split_path, split_type, target_dir, category):
    """处理train/test/val目录下的文件"""
    files = [f for f in os.listdir(split_path) 
             if os.path.isfile(os.path.join(split_path, f)) and 
             not f.endswith('.yaml')]  # 排除metadata文件
    
    # 使用正则表达式严格匹配文件名格式
    import re
    image_pattern = re.compile(r'^\d+_image_5\.png$')
    depth_pattern = re.compile(r'^\d+_depth\.png$')
    mask_pattern = re.compile(r'^\d+_mask\.png$')
    
    for filename in tqdm(files, desc=f"{category}/{split_type}", leave=False):
        # 提取数字前缀
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
            continue  # 跳过不符合格式的文件
            
        # 处理test的metadata
        if split_type == 'test_public':
            metadata_file = f"{prefix}_metadata.yaml"
            metadata_path = os.path.join(split_path, metadata_file)
            quality = 'good'  # 默认值
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = yaml.safe_load(f)
                    quality = 'bad' if metadata.get('anomalous', 0) == 1 else 'good'
                except:
                    pass
        else:
            quality = 'good'
        
        #if split_type == 'test_public':
        #    split_type = 'test'
        # 确定目标子目录
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
    """重新编号所有文件（从0开始）"""
    print("\n正在重新编号文件...")
    for root, dirs, files in os.walk(target_dir):
        if not files:
            continue
            
        # 只处理目标文件
        target_files = [f for f in files if any(f.endswith(ext) for ext in 
                      ['_image_5.png', '_depth.png', '_mask.png'])]
        if not target_files:
            continue
            
        # 按原始前缀分组
        file_groups = {}
        for f in target_files:
            prefix = f.split('_')[0]
            if prefix not in file_groups:
                file_groups[prefix] = []
            file_groups[prefix].append(f)
        
        # 按原始前缀排序后重新编号
        sorted_prefixes = sorted(file_groups.keys(), key=lambda x: int(x))
        for new_num, old_prefix in enumerate(sorted_prefixes):
            for old_name in file_groups[old_prefix]:
                parts = old_name.split('_')
                #parts[0] = f"{new_num:03d}"  # 保持4位数字，前面补零
                #new_name = '_'.join(parts)
                new_name = f"{new_num:03d}.png"  # 保持4位数字，前面补零
                
                old_path = os.path.join(root, old_name)
                new_path = os.path.join(root, new_name)
                os.rename(old_path, new_path)

def main():
    source_dir = '/home/wb/dataset-eyecandies'
    target_dir = '/home/wb/Eye/eyecandies'
    
    print("="*50)
    print("数据集处理工具")
    print(f"源目录: {os.path.abspath(source_dir)}")
    print(f"目标目录: {os.path.abspath(target_dir)}")
    print("="*50 + "\n")
    
    # 初始化目标目录
    if os.path.exists(target_dir):
        print("清空现有目标目录...")
        shutil.rmtree(target_dir)
    os.makedirs(target_dir)
    
    # 处理文件
    process_directory(source_dir, target_dir)
    
    # 重新编号
    renumber_files(target_dir)
    
    print("\n" + "="*50)
    print("处理完成！结果已保存到:")
    print(os.path.abspath(target_dir))
    print("目录结构示例:")
    print("target/类别/train/good/rgb/0000_image_5.png")
    print("target/类别/test/bad/xyz/0001_depth.png")
    print("="*50)

if __name__ == "__main__":
    try:
        import yaml
        from tqdm import tqdm
    except ImportError as e:
        print(f"错误: 缺少依赖库 - {e}")
        print("请先运行: pip install PyYAML tqdm")
        exit(1)
        
    main()
