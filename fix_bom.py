with open('data/francia.json', 'rb') as f:
    content = f.read()
if content.startswith(b'\xef\xbb\xbf'):
    content = content[3:]
with open('data/francia.json', 'wb') as f:
    f.write(content)
print("✅ BOM eliminado de francia.json")
