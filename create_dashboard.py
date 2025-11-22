#!/usr/bin/env python3
"""
Create a summary dashboard from the C inventory
"""
import csv
import collections

# Read the CSV
inventory = []
with open('c_modernization_tracker.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        inventory.append(row)

# Generate summary statistics
print("=== C Modernization Dashboard ===")
print(f"Total C/C++ files: {len(inventory)}")

# Complexity breakdown
complexity = collections.Counter([item['complexity'] for item in inventory])
print(f"\n📈 Complexity Breakdown:")
for comp, count in complexity.most_common():
    print(f"   {comp}: {count} files")

# Priority breakdown  
priority = collections.Counter([item['priority'] for item in inventory])
print(f"\n🎯 Priority Breakdown:")
for prio, count in priority.most_common():
    print(f"   {prio}: {count} files")

# Purpose breakdown
purpose = collections.Counter([item['purpose'] for item in inventory])
print(f"\n🔬 Purpose Breakdown:")
for purp, count in purpose.most_common():
    print(f"   {purp}: {count} files")

# File type breakdown
file_type = collections.Counter([item['file_type'] for item in inventory])
print(f"\n📄 File Type Breakdown:")
for ftype, count in file_type.most_common():
    print(f"   {ftype}: {count} files")

# Total lines of C code
total_lines = sum(int(item['lines']) for item in inventory if item['lines'])
print(f"\n📊 Total Lines of C Code: {total_lines:,}")

# Quick wins (Low complexity, Low priority)
quick_wins = [item for item in inventory if item['complexity'] == 'Low' and item['priority'] == 'Low']
print(f"\n🚀 Quick Wins Available: {len(quick_wins)} files")

if quick_wins:
    print("   Suggested starting points:")
    for item in quick_wins[:5]:
        print(f"   - {item['filename']} ({item['purpose']})")

