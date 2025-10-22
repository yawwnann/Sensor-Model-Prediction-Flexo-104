"""
Script to fix indentation in dashboard.py - remove container wrapping
"""

def fix_dashboard_indentation():
    file_path = r"c:\Users\HP\Documents\Belajar python\Digital Twin\Sistem2\dashboard.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_line = False
    
    for i, line in enumerate(lines):
        # Skip lines with container wrapping
        if 'with oee_detail_container.container():' in line:
            skip_line = True
            continue
        elif 'with components_container.container():' in line:
            skip_line = True
            continue
        elif 'with trends_container.container():' in line:
            skip_line = True
            continue
        elif 'with fmea_container.container():' in line:
            skip_line = True
            continue
        elif 'with footer_container.container():' in line:
            skip_line = True
            continue
        
        # Fix excessive indentation (12 spaces -> 0, 8 spaces -> 4)
        if line.startswith('            '):  # 12 spaces
            line = line[12:]  # Remove all
        elif line.startswith('        ') and i > 420:  # 8 spaces after line 420
            # Check if it should be 4 spaces or no indent
            stripped = line.lstrip()
            if stripped.startswith('with col'):
                line = line[4:]  # Keep 4 spaces
            elif stripped.startswith('st.'):
                line = line[4:]  # Keep 4 spaces  
            elif stripped.startswith('availability'):
                line = stripped  # No indent
            elif stripped.startswith('performance'):
                line = stripped  # No indent
            elif stripped.startswith('quality'):
                line = stripped  # No indent
            elif stripped.startswith('avg_'):
                line = stripped  # No indent
            elif stripped.startswith('calculated_'):
                line = stripped  # No indent
            elif stripped.startswith('col_'):
                line = stripped  # No indent
            elif stripped.startswith('fig'):
                line = line[4:]  # Keep 4 spaces
            elif stripped.startswith('for'):
                line = stripped  # No indent
            elif stripped.startswith('if'):
                line = stripped  # No indent
            elif stripped.startswith('trend_'):
                line = line[4:]  # Keep 4 spaces
            elif stripped.startswith('logs_'):
                line = line[4:]  # Keep 4 spaces
            elif stripped.startswith('fmea_'):
                line = line[4:]  # Keep 4 spaces
            elif stripped.startswith('else:'):
                line = stripped  # No indent
            elif stripped.startswith('data '):
                line = '    ' + stripped  # 4 spaces
        
        new_lines.append(line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✓ Fixed dashboard.py indentation")
    print(f"  Removed {len(lines) - len(new_lines)} container wrapper lines")
    print(f"  Total lines: {len(new_lines)}")

if __name__ == "__main__":
    fix_dashboard_indentation()
