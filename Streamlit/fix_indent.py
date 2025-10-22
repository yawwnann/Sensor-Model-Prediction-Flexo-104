#!/usr/bin/env python3
# Fix indentation in dashboard.py

with open('dashboard.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

fixed_lines = []
for i, line in enumerate(lines):
    # Lines starting from 397 that have 8 spaces, reduce to 4 spaces
    if i >= 396:  # Line 397 is index 396
        if line.startswith('        ') and not line.startswith('            '):
            # Remove 4 spaces
            fixed_lines.append(line[4:])
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

with open('dashboard.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Indentation fixed!")
