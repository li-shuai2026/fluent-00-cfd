# UV-CIPP gravity-pipe CFD reproducibility package

Reproducible CFD data and scripts for gravity-pipe flow simulation (ANSYS Fluent).

This release contains saved ANSYS Fluent models and numerical evidence for a 30 m gravity pipe: three meshes (225,000 / 450,000 / 900,000 cells), a common coarse-grid 150 s starting field, three-grid 150–160 s continuations, baseline history, residuals, dense monitoring, timestep and outlet-boundary comparisons, and an analytical Manning roughness sweep.

## Start here

- Chinese guide: `docs/START_HERE_ZH.md`.
- Model settings verified from saved HDF5 files: `docs/MODEL_AND_NUMERICS.md`.
- Reproduction commands: `docs/REPRODUCE.md`.
- Definitions and signs: `docs/sign_conventions.md` and `metadata/data_dictionary.csv`.
- Figure/table/source index: `metadata/figure_table_map.csv`.
- Pending publication steps: `docs/PUBLISH_TO_GITHUB.md`.

## Verify the tabular results (Python standard library only)

From the extracted `fluent-pipe-reproducibility` directory:

```sh
python scripts/verify_and_summarize.py
```

Outputs go to `reproduced/statistics/`. To verify all supplied files in the main package, add `--verify-files`. The smaller source archive omits `models/`; its corresponding checksum manifest is filtered accordingly.

## Files and release assets

| Location | Contents |
| --- | --- |
| `models/mesh` | Three supplied meshes |
| `models/baseline_150s` | Common 150 s case/data pair |
| `models/three_grid` | Three final 160 s case/data pairs |
| `models/additional_160s` | Dense coarse, two smaller timesteps, three outlet scenarios |
| `data/` | Native/processed CSVs, residual transcripts, reference Excel workbooks |
| `figures/` | Supplied manuscript figures 3-1 through 3-6, available formats |
| `summary/` | Recomputed numerical summaries |
| `metadata/` | Provenance, definitions, saved-state audit and checksums |
| `scripts/` | Statistics checks and a portable three-grid Fluent runner |

The main archive includes the model files above. The source archive omits all `models/` files and supports tabular verification without a Fluent license. Full intermediate fields are provided separately in **11 independently extractable checkpoint ZIPs** (120 case/data pairs, 40 per grid), listed in `metadata/checkpoint_archives.csv`. Extract selected archives alongside the main archive; all share the same top-level directory.

## Evidence and interpretation

Three-grid monitors contain 40 records per grid at 0.25 s intervals; step-final residuals contain 1,000 records per grid. The separate dense coarse run contains 200 observations at 0.05 s intervals. No intermediate observations have been fabricated or interpolated. Baseline monitoring starts at 33.55 s; a complete 0–150 s time series is not available here.

Figure 3-3 and its CSV use the corrected exact-section water-depth extraction. The archived Excel workbooks are preserved reference versions and may contain older labels or extraction results; the corrected CSVs, source index and saved-state audit take priority. Roughness Figure 3-6 is an analytical Manning calculation, not a roughness CFD campaign. Numerical comparisons do not constitute field validation.

## Re-run a solver case

Fluent 2026 R1 and a valid local license are required. Preview without launching:

```sh
python scripts/rerun_three_grid.py --grid coarse
```

See `docs/REPRODUCE.md` before adding `--execute`. This packaging revision tested syntax, tabular analysis and dry-run behavior; it did not execute a new solver run.

## Attribution and reuse

See `licenses/README.md`. Licenses are proposed, not adopted. Fill the citation template only after the author/project details are confirmed. ANSYS software and a solver license are not distributed.

Replot the six source comparisons with `python scripts/plot_source_comparisons.py`; see `docs/PLOTTING.md`. Original manuscript exports remain separate.
