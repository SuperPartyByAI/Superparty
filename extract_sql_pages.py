import re
import os

sql_file = r'C:\Users\ursac\Downloads\hosterion-backup\backup-3.22.2026_03-08-34_wowparty\mysql\wowparty_wp631.sql'
out_dir = r'C:\Users\ursac\Superparty\wowparty_old_pages'

os.makedirs(out_dir, exist_ok=True)

print(f"Reading SQL file: {sql_file}")
try:
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Simple regex to extract post content. 
    # Look for patterns matching: (ID, author, date, date_gmt, 'content', 'title', 'excerpt', 'status'='publish', ..., 'post_type'='page')
    # Since mysqldump escapes single quotes with \', we can split by `),(` and analyze
    
    # Find all INSERT INTO wp_posts statements
    inserts = re.finditer(r"INSERT INTO `[^`]*?posts` VALUES (.*?);", content, re.DOTALL)
    
    pages_found = 0
    for insert in inserts:
        values_str = insert.group(1)
        # Hacky split to get individual rows
        rows = values_str.split("),(")
        for row in rows:
            if "'publish'" in row and "'page'" in row:
                # Extract title and content roughly
                parts = row.split("','")
                if len(parts) > 5:
                    title = parts[5].replace("'", "").replace("\\", "").strip()
                    html_content = parts[4]
                    
                    # Clean up the file name
                    safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                    safe_title = safe_title.replace(" ", "_")
                    if not safe_title:
                        safe_title = f"page_{pages_found}"
                        
                    with open(os.path.join(out_dir, f"{safe_title}.html"), 'w', encoding='utf-8') as out_f:
                        out_f.write(html_content)
                    pages_found += 1
                    print(f"Extracted page: {safe_title}")
                    
    print(f"Done! {pages_found} pages extracted to {out_dir}")
except Exception as e:
    print(f"Error: {e}")
