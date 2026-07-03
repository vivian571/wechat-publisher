import os

root_dir = r"f:\公众号写作\小说\撰写提示词书籍"
part1_folders = [
    "第一章引言",
    "第二章提示词基础",
    "第三章高级指令技巧",
    "第四章场景分类提示词大全"
]
part2_folders = [
    "第五章提示词优化与迭代调试",
    "第六章主流模型适配指南",
    "第七章从提示词到AI Agent",
    "附录"
]

def merge_files(folder_list, output_filename):
    print(f"Creating {output_filename}...")
    try:
        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for folder in folder_list:
                folder_path = os.path.join(root_dir, folder)
                if not os.path.exists(folder_path):
                    print(f"Warning: Folder not found: {folder}")
                    continue
                
                print(f"Processing folder: {folder}")
                # User requested to remove folder titles like "第一章..."
                # outfile.write(f"\n\n{'='*30}\n{folder}\n{'='*30}\n\n")
                
                # Get and sort files
                try:
                    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
                    files.sort() 
                    
                    import re
                    
                    for filename in files:
                        file_path = os.path.join(folder_path, filename)
                        print(f"  Adding file: {filename}")
                        
                        base_name = filename[:-4]
                        # Extract number from filename (e.g. "1.1")
                        file_num_match = re.match(r"^(\d+\.\d+)", base_name)
                        file_num = file_num_match.group(1) if file_num_match else None
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content_str = infile.read()
                                # Remove all '#' characters
                                content_str = content_str.replace('#', '')
                                
                                lines = content_str.split('\n')
                                new_lines = []
                                header_found = False
                                
                                for line in lines:
                                    stripped = line.strip()
                                    # Remove lines like 【第 1 章 - ...】
                                    if re.match(r"^【第\s*\d+\s*章\s*-.*】$", stripped):
                                        continue
                                        
                                    # Try to find and replace the chapter title in the text
                                    # We look for a line starting with the file number (e.g. "1.1")
                                    if not header_found and file_num:
                                        # Check if line starts with specific number followed by space or non-digit
                                        # This prevents 1.1 matching 1.10
                                        if re.match(rf"^{re.escape(file_num)}(\s+|$|\D)", stripped):
                                            # Replace "1.1" with "第1.1章"
                                            # We use the rest of the line as is
                                            rest_of_line = stripped[len(file_num):]
                                            new_title = f"第{file_num}章{rest_of_line}"
                                            new_lines.append(new_title)
                                            header_found = True
                                            continue
                                    
                                    new_lines.append(line)
                                
                                # If we didn't find the title in text, use filename as header
                                if not header_found:
                                    match = re.match(r"^(\d+\.\d+)\s*(.*)$", base_name)
                                    if match:
                                        num = match.group(1)
                                        txt = match.group(2)
                                        # Ensure space matching user preference if implied
                                        header = f"第{num}章 {txt}"
                                    else:
                                        header = base_name
                                    outfile.write(f"\n\n{header}\n\n")
                                else:
                                    outfile.write("\n\n") # Separation

                                outfile.write("\n".join(new_lines))
                                
                        except Exception as e:
                            print(f"  Error reading/processing file {filename}: {e}")
                            outfile.write(f"\n[ERROR READING FILE: {filename}]\n")
                            
                except Exception as e:
                    print(f"  Error listing directory {folder}: {e}")
                    
        print(f"Finished creating {output_filename}")
        
    except Exception as e:
        print(f"CRITICAL ERROR creating {output_filename}: {e}")

if __name__ == "__main__":
    
    part1_path = os.path.join(root_dir, "Book_Part1.txt")
    merge_files(part1_folders, part1_path)
    
    part2_path = os.path.join(root_dir, "Book_Part2.txt")
    merge_files(part2_folders, part2_path)
