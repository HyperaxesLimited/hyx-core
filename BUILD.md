# Build Instructions

Questo progetto supporta **due build diverse**:
- **pcd-hyperaxes** (full) - Include tutti i moduli e dipendenze
- **pcd-hyperaxes-core** - Versione minimale per container

## Building the Full Package (pcd-hyperaxes)

Include tutti i moduli: `core`, `llm`, `visualization`, `tui`, `output`, `utils`

```bash
python -m build
# Output: dist/pcd_hyperaxes-1.0.0-py3-none-any.whl
```

### Installazione
```bash
pip install dist/pcd_hyperaxes-1.0.0-py3-none-any.whl
```

### Entry Points Disponibili
```bash
pcd-hyperaxes           # CLI principale
pcd-hyperaxes-tui       # Text User Interface
pcd-hyperaxes-chat      # LLM Chat Interface
```

## Building the Core Package (pcd-hyperaxes-core)

Include solo: `core`, `output`, `utils`, `cli` (senza `llm`, `visualization`, `tui`)

Dipendenze minimali:
- numpy >= 1.21.0
- scipy >= 1.7.0
- matplotlib >= 3.5.0
- open3d >= 0.17.0
- laspy >= 2.3.0

**NOTA**: Esclude `ollama` e `textual` per ridurre il footprint

```bash
python build_core.py
# Output: dist/pcd_hyperaxes_core-1.0.0-py3-none-any.whl
```

### Installazione
```bash
pip install dist/pcd_hyperaxes_core-1.0.0-py3-none-any.whl
```

### Entry Points Disponibili
```bash
pcd-hyperaxes           # CLI principale (con visualization disabilitata)
```

## Differenze tra i Due Build

| Feature | pcd-hyperaxes (full) | pcd-hyperaxes-core |
|---------|---------------------|---------------------|
| Modulo `core` | ✓ | ✓ |
| Modulo `output` | ✓ | ✓ |
| Modulo `utils` | ✓ | ✓ |
| Modulo `llm` | ✓ | ✗ |
| Modulo `visualization` | ✓ | ✗ |
| File `tui.py` | ✓ | ✗ |
| Dipendenza `ollama` | ✓ | ✗ |
| Dipendenza `textual` | ✓ | ✗ |
| Entry points | 3 | 1 |
| Dimensione stimata | ~200 MB | ~150 MB |

## Uso Raccomandato

### Full Package (pcd-hyperaxes)
Usa questo per:
- Sviluppo locale
- Installazione completa con tutte le funzionalità
- Quando hai bisogno di TUI o LLM chat
- Quando vuoi le visualizzazioni grafiche

```bash
pip install -e .  # Editable install per sviluppo
```

### Core Package (pcd-hyperaxes-core)
Usa questo per:
- Container Docker/Kubernetes
- Servizi distribuiti
- Lambda functions / Serverless
- Quando vuoi minimizzare le dipendenze
- Quando non hai bisogno di GUI

```bash
pip install pcd-hyperaxes-core
```

## Import Path

**IMPORTANTE**: Entrambi i package usano lo stesso import path!

```python
from pcd_hyperaxes import load_point_cloud, preprocess_point_cloud
from pcd_hyperaxes.core.analysis import compute_cloud_distances
from pcd_hyperaxes.config import AnalysisConfig
```

## Verifica Build

### Test Build Completo
```bash
# Build
python -m build

# Install
pip install dist/pcd_hyperaxes-1.0.0-py3-none-any.whl

# Test entry points
pcd-hyperaxes --version
pcd-hyperaxes-tui --help
pcd-hyperaxes-chat --help

# Verifica import completi
python -c "from pcd_hyperaxes.llm import chat"
python -c "from pcd_hyperaxes.visualization import viewer"
```

### Test Build Core
```bash
# Build
python build_core.py

# Install in ambiente separato
python -m venv test_core
source test_core/bin/activate  # Linux/Mac
# oppure: test_core\Scripts\activate  # Windows

pip install dist/pcd_hyperaxes_core-1.0.0-py3-none-any.whl

# Test entry point
pcd-hyperaxes --version

# Verifica che llm/visualization NON siano presenti
python -c "from pcd_hyperaxes.llm import chat"  # Deve fallire
python -c "from pcd_hyperaxes.visualization import viewer"  # Deve fallire

# Verifica che le funzioni core funzionino
python -c "from pcd_hyperaxes import load_point_cloud, preprocess_point_cloud"

# Verifica dipendenze installate
pip list | grep -E "(ollama|textual)"  # NON devono essere presenti
pip list | grep -E "(numpy|scipy|open3d|laspy)"  # Devono essere presenti
```

### Test End-to-End Core
```bash
# Con il package core, eseguire analisi senza visualization
pcd-hyperaxes source.ply target.ply --no-plot -o results.json
```

## Sviluppo

### Setup Ambiente di Sviluppo
```bash
# Clone repository
git clone <repo-url>
cd 3d-python-hyperaxes

# Crea virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac

# Installa in modalità editable (full)
pip install -e .

# Installa dipendenze di sviluppo
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest tests/
```

### Linting
```bash
ruff check .
mypy .
```

## Dockerfile Example (Core Build)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copia solo i file necessari per il build core
COPY pyproject-core.toml pyproject.toml
COPY MANIFEST-core.in MANIFEST.in
COPY pcd_hyperaxes/ pcd_hyperaxes/

# Installa dipendenze di build
RUN pip install build

# Build core wheel
RUN python -m build --wheel

# Installa il wheel
RUN pip install dist/pcd_hyperaxes_core-*.whl

# Cleanup
RUN rm -rf dist build *.egg-info

CMD ["pcd-hyperaxes", "--help"]
```

## Troubleshooting

### ImportError: Visualization module not available
Questo è normale nel core build. Usa `--no-plot` per disabilitare la visualizzazione:

```bash
pcd-hyperaxes source.ply target.ply --no-plot
```

### Module 'pcd_hyperaxes_core' not found
Assicurati di usare il nuovo nome del modulo `pcd_hyperaxes`:

```python
# ✗ Vecchio (non funziona più)
from pcd_hyperaxes_core import load_point_cloud

# ✓ Nuovo
from pcd_hyperaxes import load_point_cloud
```

### Build script fails with missing pyproject-core.toml
Assicurati di essere nella root directory del progetto:

```bash
cd /Users/nicolasabino/dev/3d-python-hyperaxes
python build_core.py
```

## Release Checklist

Prima di creare una release:

1. ✓ Aggiornare version in `pyproject.toml` e `pyproject-core.toml`
2. ✓ Eseguire test completi
3. ✓ Build entrambi i package
4. ✓ Test install di entrambi i package
5. ✓ Aggiornare CHANGELOG.md
6. ✓ Tag release in git
7. ✓ Upload wheels su PyPI (se pubblico)

```bash
# Build entrambi
python -m build
python build_core.py

# Upload su PyPI (opzionale)
twine upload dist/pcd_hyperaxes-*.whl
twine upload dist/pcd_hyperaxes_core-*.whl
```
