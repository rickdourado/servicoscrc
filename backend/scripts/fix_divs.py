import os

files_to_fix = [
    'frontend/wireframes/tobe_wizard_base.html',
    'frontend/wireframes/tobe_sossego.html'
]

pattern = """            </div>\n        </div>\n            </div>\n        <div class="step-content-section" id="step3" style="display: none;">"""
replacement = """            </div>\n        </div>\n        <div class="step-content-section" id="step3" style="display: none;">"""

for filepath in files_to_fix:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if pattern in content:
        content = content.replace(pattern, replacement)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"Pattern not found in {filepath}")
