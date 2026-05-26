import os

ignore_dirs = {'.git', 'node_modules', 'target', 'dist', '.next', 'bin', 'obj', '.svelte-kit'}

found = []
for root, dirs, files in os.walk(r'c:\Users\ADMIN\Desktop'):
    # prune directory search
    dirs[:] = [d for d in dirs if d not in ignore_dirs]
    for d in dirs:
        if 'murdoku' in d.lower():
            found.append(os.path.join(root, d))
    for f in files:
        if 'murdoku' in f.lower():
            found.append(os.path.join(root, f))

print("Found items:")
for item in found:
    print(item)
