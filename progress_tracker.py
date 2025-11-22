#!/usr/bin/env python3
"""
Track modernization progress over time
"""
import csv
import datetime
import json

def load_inventory():
    inventory = []
    with open('c_modernization_tracker.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            inventory.append(row)
    return inventory

def update_progress(filename, new_status, notes=""):
    """Update the status of a specific file"""
    inventory = load_inventory()
    
    for item in inventory:
        if item['filename'] == filename or item['filepath'] == filename:
            item['status'] = new_status
            item['notes'] = notes
            item['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d')
            break
    
    # Write back to CSV
    with open('c_modernization_tracker.csv', 'w', newline='', encoding='utf-8') as f:
        fieldnames = inventory[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(inventory)
    
    print(f"✅ Updated {filename} to status: {new_status}")

def show_progress():
    """Show current modernization progress"""
    inventory = load_inventory()
    
    status_counts = collections.Counter([item['status'] for item in inventory])
    total = len(inventory)
    
    print("=== Modernization Progress ===")
    for status, count in status_counts.most_common():
        percentage = (count / total) * 100
        print(f"   {status}: {count}/{total} files ({percentage:.1f}%)")
    
    # Calculate completion percentage (considering "Completed" and "In Progress" as progress)
    completed = status_counts.get('Completed', 0)
    in_progress = status_counts.get('In Progress', 0)
    total_progress = completed + (in_progress * 0.5)  # Count in-progress as half
    overall_percentage = (total_progress / total) * 100
    
    print(f"\n📊 Overall Progress: {overall_percentage:.1f}%")
    print(f"🎯 Next recommended file:")
    
    # Recommend next file to work on
    not_started = [item for item in inventory if item['status'] == 'Not Started']
    if not_started:
        # Prioritize by complexity and priority
        next_file = min(not_started, key=lambda x: (
            {'High': 0, 'Medium': 1, 'Low': 2}[x['priority']],
            {'High': 0, 'Medium': 1, 'Low': 2}[x['complexity']],
            int(x['lines'])
        ))
        print(f"   {next_file['filename']} - {next_file['purpose']} (Priority: {next_file['priority']})")

if __name__ == "__main__":
    import collections
    show_progress()

