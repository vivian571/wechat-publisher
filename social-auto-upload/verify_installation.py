import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(os.getcwd())

print("=== Social Auto Upload Verification ===")

# 1. Check dependencies
print("\n[1] Checking Dependencies:")
try:
    import openai
    print("  [OK] openai")
except ImportError:
    print("  [FAIL] openai (pip install openai)")

try:
    import anthropic
    print("  [OK] anthropic")
except ImportError:
    print("  [FAIL] anthropic (pip install anthropic)")

try:
    import PIL
    print("  [OK] pillow")
except ImportError:
    print("  [FAIL] pillow (pip install pillow)")

# 2. Check FFmpeg
print("\n[2] Checking FFmpeg:")
import shutil
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    print(f"  [OK] ffmpeg found at {ffmpeg_path}")
else:
    print("  [WARN] ffmpeg not found in PATH")

# 3. Check New Modules
print("\n[3] Checking New Modules:")
try:
    from utils import ai_optimizer
    print("  [OK] utils.ai_optimizer")
except ImportError as e:
    print(f"  [FAIL] utils.ai_optimizer: {e}")

try:
    from utils import cover_generator
    print("  [OK] utils.cover_generator")
except ImportError as e:
    print(f"  [FAIL] utils.cover_generator: {e}")

try:
    from utils import matrix_bridge
    print("  [OK] utils.matrix_bridge")
except ImportError as e:
    print(f"  [FAIL] utils.matrix_bridge: {e}")
    
try:
    from utils import files_times
    print("  [OK] utils.files_times")
except ImportError as e:
    print(f"  [FAIL] utils.files_times: {e}")

# 4. Check Config
print("\n[4] Checking Configuration:")
try:
    import conf
    print(f"  [OK] conf module loaded from {conf.__file__}")
    
    if hasattr(conf, 'AI_OPTIMIZER_ENABLED'):
        print(f"  [OK] AI_OPTIMIZER_ENABLED = {conf.AI_OPTIMIZER_ENABLED}")
    else:
        print("  [WARN] AI_OPTIMIZER_ENABLED not found in conf.py")
        
    if hasattr(conf, 'COVER_GENERATOR_ENABLED'):
        print(f"  [OK] COVER_GENERATOR_ENABLED = {conf.COVER_GENERATOR_ENABLED}")
    else:
        print("  [WARN] COVER_GENERATOR_ENABLED not found in conf.py")
        
except ImportError:
    print("  [FAIL] conf module not found (please copy conf.example.py to conf.py)")

print("\n=== Verification Complete ===")
