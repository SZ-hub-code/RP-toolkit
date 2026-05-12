# RP-toolkit

Toolkit Python de radioprotection pour calculs de dose, attenuation de blindage,
decroissance radioactive, et workflows ALARA.

## Installation

### 1) Cloner et entrer dans le projet

```bash
git clone <repo-url>
cd rp-toolkit
```

### 2) Installer les dependances

Option editable (recommande en dev):

```bash
pip install -e .
```

Option requirements pinned:

```bash
pip install -r requirements.txt
```

## Exemples rapides

### Base nucleaire

```python
from rp_toolkit.core.nuc_db import NucDB

db = NucDB()
cs137 = db.get("Cs-137")
print(cs137.half_life("y"))
```

### Debit de dose gamma (1/r^2)

```python
from rp_toolkit.core.dose_rate import DoseScenario

scenario = DoseScenario(nuclide="Cs-137", activity_bq=2e9, distance_m=2.0)
print(scenario.dose_rate_uSv_h())
```

### Decroissance

```python
from rp_toolkit.core.decay import decay_activity

a_t = decay_activity(a0_bq=1e6, half_life_s=30.17 * 365.25 * 24 * 3600, time_s=24 * 3600)
print(a_t)
```

## Lancer l'application Streamlit

```bash
streamlit run app/main.py
```

## Structure

Le projet suit une separation claire:

- `rp_toolkit/core`: physique pure, sans UI ni I/O.
- `rp_toolkit/data`: donnees statiques embarquees.
- `rp_toolkit/io`: lecture/ecriture donnees externes.
- `rp_toolkit/viz`: visualisation (matplotlib/streamlit).
- `app`: interface Streamlit multipages.
- `tests`: suite pytest.
