import sys
import os

def process_file(file_path):
    encodings = ['utf-8', 'gb18030']
    content = None
    read_encoding = None

    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
            read_encoding = enc
            print(f"Read {file_path} using {enc}")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return

    if content is None:
        print(f"Failed to decode {file_path} with supported encodings.")
        return

    new_content = content.replace('*', '')

    try:
        # Write back using the same encoding if possible, or utf-8
        write_enc = read_encoding if read_encoding else 'utf-8'
        with open(file_path, 'w', encoding=write_enc) as f:
            f.write(new_content)
        print(f"Successfully removed asterisks from {file_path}")
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_asterisks.py <file_path>")
    else:
        process_file(sys.argv[1])
