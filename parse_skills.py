#!/usr/bin/env python3
import re
import sys
import json
from pathlib import Path

# Input: JSON array of skill texts from stdin
def parse_skill_text(text):
    # Example: "Gog/gogGoogle Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs.by@steipete 30.6k★ 2051 v"
    # Some have newlines, extra spaces missing due to CSS
    # Try to extract parts
    # Find the first slash to separate name/slug
    if '/' not in text:
        return None
    # Split by '/' but name may contain spaces
    # Actually pattern: name/slugDescriptionby@author downloads★ stars version
    # Use regex
    # Regex pattern: (.*?)/(.*?)(by@[^\s]+)?\s*([\d\.]+[kK]?)\s*★\s*(\d+)\s*(\d+)\s*v\s*$
    # But description is between slug and "by@"
    # Let's try simpler: split by 'by@'
    parts_by = text.split('by@')
    if len(parts_by) < 2:
        return None
    before_by = parts_by[0]
    after_by = parts_by[1]
    # before_by: name/slugDescription
    # Extract name and slug
    if '/' not in before_by:
        return None
    name_slug, description = before_by.split('/', 1)
    name = name_slug.strip()
    # slug is up to next capital letter or end
    # Slug is alphanumeric with hyphens, but here it's lowercase letters and hyphens
    # Find where description starts (first capital letter after slug)
    # Assume slug is lowercase letters, hyphens, maybe digits
    slug_match = re.match(r'^([a-z0-9\-]+)', description)
    if slug_match:
        slug = slug_match.group(1)
        desc_start = slug_match.end()
        desc_text = description[desc_start:].strip()
    else:
        slug = ''
        desc_text = description.strip()
    
    # After "by@": author rest
    # Pattern: author downloads★ stars version
    # Extract downloads (number with k), stars (digits), version (digits)
    after_by_parts = after_by.strip().split()
    if len(after_by_parts) < 3:
        downloads = '0'
        stars = '0'
        version = '0'
    else:
        downloads = after_by_parts[0]
        # Find stars: after ★
        # Actually stars is after ★ which might be in previous part
        # Join and regex
        combined = ' '.join(after_by_parts)
        star_match = re.search(r'★\s*(\d+)', combined)
        stars = star_match.group(1) if star_match else '0'
        # version is digits before 'v'
        version_match = re.search(r'(\d+)\s*v', combined)
        version = version_match.group(1) if version_match else '0'
    
    return {
        'name': name,
        'slug': slug,
        'description': desc_text,
        'downloads': downloads,
        'stars': int(stars),
        'version': version
    }

def main():
    # Read JSON from stdin
    data = sys.stdin.read()
    try:
        texts = json.loads(data)
    except json.JSONDecodeError:
        # Maybe it's a Python list literal
        texts = eval(data)
    
    skills = []
    for text in texts:
        if text == 'Skills':
            continue
        parsed = parse_skill_text(text)
        if parsed:
            skills.append(parsed)
        else:
            # Fallback: store raw text
            skills.append({
                'name': 'Unknown',
                'slug': '',
                'description': text,
                'downloads': '0',
                'stars': 0,
                'version': '0'
            })
    
    # Sort by stars descending (already sorted but ensure)
    skills.sort(key=lambda x: x['stars'], reverse=True)
    
    # Keep top 100
    skills = skills[:100]
    
    # Output as JSON
    print(json.dumps(skills, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()