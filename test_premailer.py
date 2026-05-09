
import os
import sys
from premailer import Premailer

# Mock CSS content
css_content = """
body {
    font-family: Georgia, serif;
    color: #333333;
    background-color: #fdf6e3;
}
h1 {
    color: #cb4b16;
}
"""

title = "Test Title"
html_body = "<h1>Hello World</h1><p>This is a test.</p>"

full_html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>{title}</title><style>{css_content}</style></head><body><article class="markdown-body">{html_body}</article></body></html>'

try:
    premailer_instance = Premailer(full_html, remove_classes=True, strip_important=False)
    result = premailer_instance.transform()
    print("--- RESULT ---")
    print(result)
except Exception as e:
    print(f"Error: {e}")
