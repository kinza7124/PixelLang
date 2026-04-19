#!/bin/bash
# Deploy documentation to GitHub Pages

# Create docs directory
mkdir -p docs
cp README.md docs/index.md
cp DOCUMENTATION.md docs/
cp pixellang_spec.html docs/

# Create index.html that redirects to spec
cat > docs/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="0; url=pixellang_spec.html">
</head>
<body>
    <p>Redirecting to <a href="pixellang_spec.html">PixelLang Specification</a>...</p>
</body>
</html>
EOF

echo "Docs ready for GitHub Pages!"
echo "Enable Pages in repo settings -> Pages -> Source -> main/docs"
