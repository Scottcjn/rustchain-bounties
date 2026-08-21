import os
import glob

def fix_workflows():
    workflow_files = glob.glob('.github/workflows/*.yml') + glob.glob('.github/workflows/*.yaml')
    for file_path in workflow_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple heuristic to add timeouts to steps if not present, or we can rewrite/patch.
        # Since we need exact python code that fixes the issue, let's ensure every `run:` step 
        # has a `timeout-minutes:` defined if it doesn't already, to prevent 15-minute silent hangs 
        # and provide clear attribution.
        
        lines = content.splitlines()
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            new_lines.append(line)
            # Check if this line starts a step (e.g., `- name:` or `- uses:` or `- run:`)
            stripped = line.strip()
            if stripped.startswith('- name:') or stripped.startswith('- run:') or stripped.startswith('- uses:'):
                # Look ahead in the current step to see if timeout-minutes is already defined
                has_timeout = False
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    # If we hit the next step or end of steps/job, stop looking
                    if next_line.strip().startswith('-') or (len(next_line) - len(next_line.lstrip()) <= len(line) - len(line.lstrip()) and not next_line.strip().startswith('#')):
                        break
                    if 'timeout-minutes:' in next_line:
                        has_timeout = True
                        break
                    j += 1
                
                if not has_timeout:
                    # Determine indentation
                    indent = len(line) - len(line.lstrip())
                    # Add timeout-minutes: 10 with proper indentation
                    # Usually steps are indented by 4 or 6 spaces
                    step_indent = ' ' * (indent + 2)
                    new_lines.append(f"{step_indent}timeout-minutes: 10")
            i += 1
            
        fixed_content = '\n'.join(new_lines) + '\n'
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

if __name__ == '__main__':
    fix_workflows()