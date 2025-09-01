#!/usr/bin/env python3
# fix_emojis.py - Corregir emojis corruptos

import sys
import os

def fix_emojis():
    file_path = "utils/graph_visualizer.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corregir emojis corruptos
    content = content.replace('gender_icon = "�"', 'gender_icon = "🤴"')
    content = content.replace('gender_icon = "�👨"', 'gender_icon = "👨"')
    content = content.replace('ego_text = "EGO"', 'ego_text = "TÚ"')
    content = content.replace('icon_x + 15', 'icon_x + 18')
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Emojis corregidos exitosamente")

if __name__ == "__main__":
    fix_emojis()
