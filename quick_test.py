"""Quick test of the compiler."""
from compiler import compile_source, lex, parse, analyze

print("Testing PixelLang Compiler...")
print()

# Test 1: Lexing
print("1. Testing lexer...")
tokens = lex("CANVAS 10 10; PIXEL 5 5 #FF0000;")
print(f"   Tokens: {len(tokens)}")
for t in tokens:
    print(f"   - {t}")
print()

# Test 2: Parsing
print("2. Testing parser...")
ast = parse(tokens)
print(f"   Statements: {len(ast.statements)}")
print()

# Test 3: Semantic analysis
print("3. Testing semantic analyzer...")
errors = analyze(ast)
print(f"   Errors: {len(errors)}")
print()

# Test 4: Full compilation
print("4. Testing full compilation...")
source = """
CANVAS 32 32;
RECT 0 0 32 32 #222222;
CIRCLE 16 16 8 #FF0000;
"""
image, errors = compile_source(source)
if image:
    print(f"   Success! Image size: {image.size}")
    image.save("test_output.png")
    print("   Saved to test_output.png")
else:
    print(f"   Errors: {errors}")

print()
print("All tests completed!")
