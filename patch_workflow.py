with open('.github/workflows/ci.yml', 'r') as f:
    content = f.read()

content = content.replace(
    'pip install pytest pytest-asyncio polars pycryptodome httpx fastapi uvicorn',
    'pip install pytest pytest-asyncio polars pycryptodome httpx fastapi uvicorn\n          pip install -r medfactory/requirements.txt'
)

with open('.github/workflows/ci.yml', 'w') as f:
    f.write(content)
