# Analisi Comparativa Tile Genova
## Confronto 03-02 vs 03-12

---

## 📋 Informazioni Generali

| Parametro | Valore |
|-----------|--------|
| **File 1** | tile_2026-03-02.xyz |
| **File 2** | tile_2026-03-12.xyz |
| **Data Analisi** | 2026-03-29 |
| **Risoluzione Scansione** | 0.25 m |
| **Voxel Size Preprocessing** | 0.25 m |

---

## 📐 Superfici Scansionate

### File 03-02 (tile_2026-03-02.xyz)

| Metrica | Valore |
|---------|--------|
| **Superficie Totale** | **2,487.50 m²** |
| **Numero di Punti** | 35,327 punti |
| **Bounds X** | [1494789.38, 1494839.13] m |
| **Bounds Y** | [4915510.38, 4915560.38] m |
| **Larghezza (X)** | 49.75 m |
| **Altezza (Y)** | 50.00 m |

### File 03-12 (tile_2026-03-12.xyz)

| Metrica | Valore |
|---------|--------|
| **Superficie Totale** | **2,487.50 m²** |
| **Numero di Punti** | 33,438 punti |
| **Bounds X** | [1494789.38, 1494839.13] m |
| **Bounds Y** | [4915510.38, 4915560.38] m |
| **Larghezza (X)** | 49.75 m |
| **Altezza (Y)** | 50.00 m |

---

## 🔄 Area Sovrapponibile

| Parametro | Valore |
|-----------|--------|
| **Superficie Overlap** | **2,487.50 m²** |
| **% rispetto a 03-02** | 100.00% |
| **% rispetto a 03-12** | 100.00% |
| **Punti 03-02 nell'overlap** | 35,327 punti |
| **Punti 03-12 nell'overlap** | 33,438 punti |

> ✅ **I due tile hanno esattamente la stessa estensione spaziale**

---

## 📊 Statistiche delle Distanze

Analisi delle distanze punto-punto tra le due scansioni:

| Statistica | Valore | Note |
|------------|--------|------|
| **Distanza Minima** | 0.0000 m | Punti identici |
| **Distanza Massima** | 6.9652 m | Differenza massima rilevata |
| **Distanza Media** | 0.4162 m | Differenza media tra i punti |
| **Distanza Mediana** | 0.1200 m | 50% dei punti hanno distanza ≤ 0.12m |
| **Deviazione Standard** | 0.7596 m | Variabilità delle distanze |

---

## 🎯 Differenze Rilevate

### Riepilogo

| Metrica | Valore |
|---------|--------|
| **Area con Differenze Significative** | **317.88 m²** |
| **% dell'Area Totale** | **12.78%** |
| **Numero di Regioni** | 2 |
| **Punti con Differenze** | 5,086 punti |

### Distribuzione dell'Area

```
Area Totale:           2,487.50 m²  ████████████████████████████████████████ 100.00%
Area Senza Differenze: 2,169.62 m²  ████████████████████████████████████     87.22%
Area con Differenze:     317.88 m²  █████                                    12.78%
```

---

## 🗺️ Dettaglio Regioni di Differenza

### Regione 1 (Principale)

| Parametro | Valore |
|-----------|--------|
| **Cluster ID** | 1 |
| **Numero di Punti** | 3,570 punti |
| **Area Stimata** | ~223 m² (70.2% delle differenze) |
| **Centroid X** | 1494812.00 m |
| **Centroid Y** | 4915517.59 m |
| **Centroid Z** | -16.35 m |

**Caratteristiche:**
- Regione più grande e significativa
- Concentrata nella parte sud-occidentale del tile
- Profondità media: -16.35 m

---

### Regione 2

| Parametro | Valore |
|-----------|--------|
| **Cluster ID** | 2 |
| **Numero di Punti** | 1,516 punti |
| **Area Stimata** | ~95 m² (29.8% delle differenze) |
| **Centroid X** | 1494827.50 m |
| **Centroid Y** | 4915545.97 m |
| **Centroid Z** | -12.97 m |

**Caratteristiche:**
- Regione secondaria
- Concentrata nella parte centrale del tile
- Profondità media: -12.97 m (più superficiale della Regione 1)

---

## 📈 Analisi Approfondita

### Distribuzione delle Differenze

- **Regione 1**: 70.2% dei punti con differenze (3,570 punti)
- **Regione 2**: 29.8% dei punti con differenze (1,516 punti)

### Confronto Profondità

| Regione | Profondità Z (m) | Differenza da Superficie |
|---------|------------------|-------------------------|
| Regione 1 | -16.35 m | Più profonda |
| Regione 2 | -12.97 m | -3.38 m rispetto a Regione 1 |

### Separazione Spaziale

| | Regione 1 | Regione 2 | Distanza |
|---|-----------|-----------|----------|
| **X** | 1494812.00 | 1494827.50 | 15.50 m |
| **Y** | 4915517.59 | 4915545.97 | 28.38 m |
| **Distanza Euclidea (XY)** | - | - | **32.31 m** |

---

## 💡 Conclusioni

### Punti Chiave

1. ✅ **Allineamento Perfetto**: I due tile hanno esattamente la stessa estensione spaziale (100% overlap)

2. ✅ **Differenze Limitate**: Solo il 12.78% dell'area presenta differenze significative (>0.9m threshold)

3. ✅ **Alta Precisione**: La distanza mediana è solo 0.12m, indicando che la maggior parte dei punti è quasi identica

4. ⚠️ **2 Regioni Distinte**: Le differenze sono concentrate in 2 aree ben separate (32.31m di distanza)

5. 📍 **Variazione Batimetrica**: Le due regioni hanno profondità diverse (-16.35m vs -12.97m)

### Possibili Cause delle Differenze

- Cambiamenti morfologici del fondale marino
- Spostamento di sedimenti
- Variazioni temporali tra le due acquisizioni (03-02 → 03-12)
- Presenza di oggetti mobili o depositi

### Qualità dei Dati

| Indicatore | Valutazione |
|------------|-------------|
| Copertura Spaziale | ⭐⭐⭐⭐⭐ Eccellente (100% overlap) |
| Densità Punti | ⭐⭐⭐⭐⭐ Alta (~14 punti/m²) |
| Coerenza | ⭐⭐⭐⭐☆ Molto buona (87% area stabile) |
| Precisione | ⭐⭐⭐⭐⭐ Eccellente (mediana 0.12m) |

---

## 📁 File Generati

- **JSON completo**: `genova_analysis_results.json`
- **Report Markdown**: `genova_tile_analysis_report.md`
- **Script Analisi**: `analyze_genova.py`

---

*Report generato automaticamente con pcd-hyperaxes*
*Data: 2026-03-29*
