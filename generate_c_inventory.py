#!/usr/bin/env python3
"""
Generate comprehensive inventory of C/C++ files for modernization tracking
"""
import os
import csv
import datetime
from pathlib import Path

def analyze_c_file(filepath):
    """Analyze a C/C++ file for modernization complexity"""
    stats = {
        'filename': os.path.basename(filepath),
        'filepath': filepath,
        'file_type': 'C' if filepath.endswith('.c') else 'C++' if filepath.endswith('.cpp') else 'Header',
        'lines': 0,
        'complexity': 'Unknown',
        'purpose': 'Unknown',
        'dependencies': [],
        'replacement_strategy': 'TBD',
        'priority': 'Medium',
        'status': 'Not Started',
        'estimated_effort': 'TBD',
        'notes': '',
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            stats['lines'] = len(lines)
            
            # Analyze purpose
            if any(keyword in content.lower() for keyword in ['fft', 'fourier', 'transform']):
                stats['purpose'] = 'FFT/Signal Processing'
                stats['complexity'] = 'High'
                stats['replacement_strategy'] = 'Numba/SciPy/External Library'
            elif any(keyword in content.lower() for keyword in ['math', 'calc', 'compute', 'algorithm']):
                stats['purpose'] = 'Mathematical Algorithm'
                stats['complexity'] = 'Medium'
                stats['replacement_strategy'] = 'NumPy/SciPy/Numba'
            elif any(keyword in content.lower() for keyword in ['file', 'io', 'read', 'write', 'parse']):
                stats['purpose'] = 'File I/O'
                stats['complexity'] = 'Low'
                stats['replacement_strategy'] = 'Python I/O'
            elif any(keyword in content.lower() for keyword in ['peak', 'pick', 'detect']):
                stats['purpose'] = 'Peak Detection'
                stats['complexity'] = 'High'
                stats['replacement_strategy'] = 'scikit-image/OpenCV'
            elif any(keyword in content.lower() for keyword in ['filter', 'smooth', 'convolution']):
                stats['purpose'] = 'Signal Filtering'
                stats['complexity'] = 'Medium'
                stats['replacement_strategy'] = 'SciPy Signal Processing'
            else:
                stats['purpose'] = 'Utility/Unknown'
                stats['complexity'] = 'Low'
                stats['replacement_strategy'] = 'Direct Python Port'
            
            # Set priority based on complexity and size
            if stats['complexity'] == 'High' and stats['lines'] > 500:
                stats['priority'] = 'High'
            elif stats['complexity'] == 'Low' and stats['lines'] < 100:
                stats['priority'] = 'Low'
                stats['estimated_effort'] = '1-2 days'
            else:
                stats['priority'] = 'Medium'
                stats['estimated_effort'] = '1 week'
            
            # Find dependencies
            import re
            includes = re.findall(r'#include\s+[<"]([^>"]+)[>"]', content)
            stats['dependencies'] = includes[:5]  # First 5 dependencies
            
    except Exception as e:
        stats['notes'] = f'Error reading file: {str(e)}'
    
    return stats

print("=== Generating C File Inventory ===")

# Find all C/C++ files
c_files = []
for root, dirs, files in os.walk('.'):
    if '.git' in root:
        continue
    for file in files:
        if file.endswith(('.c', '.cpp', '.h', '.hpp')):
            c_files.append(os.path.join(root, file))

print(f"Found {len(c_files)} C/C++ files")

# Analyze each file
inventory = []
for filepath in c_files:
    print(f"Analyzing: {filepath}")
    inventory.append(analyze_c_file(filepath))

# Generate CSV
csv_filename = 'c_modernization_tracker.csv'
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = [
        'filename', 'filepath', 'file_type', 'lines', 'complexity', 
        'purpose', 'dependencies', 'replacement_strategy', 'priority',
        'status', 'estimated_effort', 'notes', 'last_updated'
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(inventory)

print(f"\n✅ Inventory generated: {csv_filename}")
print(f"📊 Summary:")
summary = {}
for item in inventory:
    summary[item['complexity']] = summary.get(item['complexity'], 0) + 1
    summary[item['priority']] = summary.get(item['priority'], 0) + 1

for key, value in summary.items():
    print(f"   {key}: {value} files")

