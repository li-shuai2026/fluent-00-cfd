# Reproduce the analysis and solver workflow

## 1. Tabular analysis without Fluent

Python 3.10+ is sufficient; the verification script uses only the standard library.

```sh
python scripts/verify_and_summarize.py --verify-files
```

Results are written to `reproduced/statistics/`. `summary/` contains the packaging-time reference outputs. The script checks counts, sampling intervals, instantaneous difference formulas and analytical Manning relationships, then reproduces grid, timestep, dense-monitor and boundary summaries. Assertions should remain enabled: do not invoke Python with `-O`.

Grid means use the saved 40-point sampling (or two consecutive 20-point windows). Timestep comparisons use trapezoidal time means over the common 150.25–160 s window, with 40 / 79 / 157 samples. Dense-coarse statistics use its own 200-point record. No smoothing or synthesized checkpoints are used.

## 2. Inspect a field in Fluent

Read a matching `.cas.h5` and `.dat.h5` pair. For the shared baseline use `models/baseline_150s/coarse_150s.*.h5`. Confirm flow time 150 s after reading data. Final fields are in `models/three_grid/` and `models/additional_160s/` at 160 s. Intermediate checkpoint packages add `models/checkpoints/{grid}/`. Keep each case/data filename stem paired. Three-grid run step 25 corresponds to physical time 150.25 s; the step in the filename is relative to the continuation.

## 3. Preview a portable three-grid rerun

Install the solver requirement in a suitable environment; provide a local Fluent 2026 R1 installation and a valid license. Model files from the main archive are required.

```sh
python -m pip install -r requirements-solver.txt
python scripts/rerun_three_grid.py --grid coarse
python scripts/rerun_three_grid.py --grid all --output reruns/reviewer_run
```

Both runner commands above are dry-runs. To actually solve:

```sh
python scripts/rerun_three_grid.py --grid all --output reruns/reviewer_run --processors 14 --execute
```

If automatic discovery fails, add `--fluent-path` followed by your local executable path. `--smoke-steps 5 --execute` is a short installation check, not a replacement for the full 1000-step comparison. All selected grids run serially. A nonempty output folder is rejected to protect previous results. The runner writes flow monitors every 25 steps, case/data checkpoints and a solver transcript; additional derived depth/residual CSVs in this release are archived post-processing results, not an automatic output guarantee of this runner.

The packaging revision verified script syntax, dry-run configuration and CSV reproducibility. It did not execute a new Fluent run or test another installation. Floating-point and parallel-partition differences may affect pointwise results on rerun; compare the same definitions and time windows.

## 4. Storage and signed flux closure

The reported instantaneous difference is 100*abs(abs(Qin)-abs(Qout))/abs(Qin). It measures inlet/outlet magnitude difference, not transient numerical conservation error. A conservation audit requires Vw(t2)-Vw(t1) plus the time integral of outward-positive water flux over all open boundaries, using synchronized outputs and the same water-volume/flux definitions. Preserve sign, include any air-inlet water crossing, and state the quadrature. A full synchronized signed-flux/storage closure table has not been added by this packaging task.
