# Energy Affordability Website - Content Workflow Guide

This guide explains how to add and edit content for the Energy Affordability website using Markdown files.

## 📁 Project Structure

```
affordability_website/
├── overview.html           # Main landing page (index.html redirects here)
├── assets/
│   ├── styles-new.css      # Global styles
│   └── (images...)         # All images go here
├── content/                # Markdown content files
│   ├── burdens.md          # Energy Burdens page content
│   ├── tool-guide.md       # Tool Guide page content
│   ├── case-studies.md     # Case Studies page content
│   ├── methodology.md      # Methodology page content
│   └── resources.md        # Resources page content
├── pages/                  # HTML page templates
│   ├── burdens.html
│   ├── tool-guide.html
│   ├── case-studies.html
│   ├── methodology.html
│   └── resources.html
└── js/
    └── content-loader.js   # Markdown parser
```

## ✍️ Content Workflow

### For Non-Technical Collaborators (Google Docs Workflow)

1. **Draft content in Google Docs** using the heading styles (Title, Heading 1, Heading 2, etc.)
2. **Use comments and Track Changes** for review and feedback
3. **Export as .docx** when ready
4. **Convert to Markdown** using:
   - Online tool: [Word to Markdown](https://word2md.com/)
   - Or Pandoc: `pandoc input.docx -f docx -t markdown -o output.md`
5. **Submit the .md file** to the content manager

### For Technical Collaborators (Direct Markdown)

1. Edit files directly in the `content/` folder
2. Use git branches for changes:
   ```bash
   git checkout -b content/update-burdens-page
   # Make edits
   git add content/burdens.md
   git commit -m "Update energy burdens statistics"
   git push origin content/update-burdens-page
   ```
3. Create a Pull Request for review

## 📝 Markdown Syntax Reference

### Headers

```markdown
# Page Title (H1)
## Section Header (H2) - Creates navigation anchors
### Subsection (H3)
#### Sub-subsection (H4)
```

### Text Formatting

```markdown
**Bold text**
*Italic text*
***Bold and italic***
```

### Lists

```markdown
- Bullet point 1
- Bullet point 2
  - Nested point

1. Numbered item
2. Another item
```

### Links

```markdown
[Link text](https://example.com)
[Internal link](tool-guide.html)
```

### Images

Basic image:
```markdown
![Alt text](image_filename.png)
```

Image with caption:
```markdown
![Alt text](image_filename.png "This is the caption")
```

Image with CSS class:
```markdown
![Alt text](image_filename.png){.custom-class}
```

### Callout Boxes

```markdown
:::note
This is a note callout box.
:::

:::warning
This is a warning callout box.
:::

:::tip
This is a tip callout box.
:::
```

### Blockquotes

```markdown
> This is a blockquote for highlighting important information.
```

### Code

Inline code: `` `code` ``

Code block:
````markdown
```python
def example():
    return "Hello"
```
````

## 🖼️ Adding Images

1. **Add image files** to the `assets/` folder
2. **Reference in Markdown** using relative paths:
   ```markdown
   ![Energy costs chart](energy_costs_chart.png "Annual energy costs by region")
   ```
3. **Supported formats:** PNG, SVG, JPG, WebP

### Image Naming Convention

Use descriptive, lowercase names with underscores:
- ✅ `energy_burden_map_2022.png`
- ✅ `tool_statistics_screenshot.png`
- ❌ `IMG_12345.png`
- ❌ `Chart (1).png`

## 🔄 Updating Content

### Quick Edits

1. Open the relevant `.md` file in `content/`
2. Make changes
3. Save and refresh the page to see updates

### Major Updates

1. Create a new git branch
2. Make changes to Markdown files
3. Submit a Pull Request for review
4. Merge after approval

## 📋 Page-Specific Guidelines

### burdens.md (Energy Burdens)
- Update statistics with real data when available
- Include source citations for key figures
- Keep figure captions descriptive

### tool-guide.md (Tool Guide)
- Add new features as they're developed
- Include step-by-step instructions
- Update screenshots when UI changes

### case-studies.md (Case Studies)
- Add new case studies as completed
- Include key findings and impact
- Link to full publications when available

### methodology.md (Methodology)
- Mark as "in progress" until publication
- Add technical details incrementally
- Link to peer-reviewed paper when published

### resources.md (Resources)
- Keep external links updated
- Verify links work periodically
- Add new publications as released

## 🧪 Testing Changes

1. Open `index-new.html` in a browser
2. Navigate to the page you edited
3. Verify:
   - Content displays correctly
   - Images load properly
   - Links work
   - Mobile layout looks good (resize browser)

## ❓ Getting Help

- **Content questions:** Contact [content manager]
- **Technical issues:** Create a GitHub issue
- **Design feedback:** Use Figma/design tool comments

## 📅 Content Calendar

| Page | Update Frequency | Last Updated |
|------|------------------|--------------|
| Energy Burdens | As data available | Dec 2024 |
| Tool Guide | With tool updates | Dec 2024 |
| Case Studies | As completed | Dec 2024 |
| Methodology | With publication | TBD |
| Resources | Quarterly | Dec 2024 |
