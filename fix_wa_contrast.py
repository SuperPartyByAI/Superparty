import os

count = 0
for root, dirs, files in os.walk('src'):
    dirs[:] = [d for d in dirs if d != 'node_modules']
    for f in files:
        if f.endswith('.astro') or f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            new = content
            # Fix WhatsApp button contrast: #25d366 cu text alb -> #128C7E (contrast 5.3:1 cu alb)
            new = new.replace('#25d366;color:#fff', '#128C7E;color:#fff')
            new = new.replace('#25d366; color:#fff', '#128C7E; color:#fff')
            new = new.replace('#25d366; color: white', '#128C7E; color: white')
            new = new.replace('#25d366; color: rgb(255, 255, 255)', '#128C7E; color: rgb(255, 255, 255)')
            new = new.replace('background:#25d366;color:white', 'background:#128C7E;color:white')
            new = new.replace('background: #25d366;', 'background: #128C7E;')
            # Layout.astro whatsapp float
            new = new.replace('background: #25d366;', 'background: #128C7E;')
            if new != content:
                with open(path, 'w', encoding='utf-8') as fh:
                    fh.write(new)
                count += 1

print(f'Fix-at {count} fisiere WhatsApp contrast')
