## Usage

Clone this repository using:
```bash
git clone https://github.com/mcgelya/dependency-graph
```

Activate `venv`:
```bash
python -m venv .venv
source .venv/bin/active
```

First install `pip-tools`:
```bash
pip install pip-tools
```

Then install `fastapi`:
```bash
pip install "fastapi[standard]"
```

Then all other requirements:
```bash
pip install -r requirements.txt
```

Then run with:

```bash
fastapi dev app/main.py 
```
