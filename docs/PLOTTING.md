# Replot source comparisons

The supplied `figures/Figure_3_*.{png,pdf,svg,tiff}` files are the existing manuscript exports in the available formats. Figure 3-3 uses the corrected exact-section source. They are not overwritten by the reproduction script.

Install Matplotlib, then run:

```sh
python -m pip install matplotlib==3.11.1
python scripts/plot_source_comparisons.py
```

This generates six source-data comparison figures in PNG/PDF/SVG under `reproduced/figures/`. The plots connect actual observations; no smoothing or interpolated observations are added. Replotted output is intended to make the underlying curves independently inspectable; it is not a pixel-identical reconstruction of manually edited manuscript art. Figure 3-1 uses separate time/depth/profile panels, and Figure 3-6 shows the full analytical parameter sweep as contours.

The residual curves in comparison 3-4 use a logarithmic y-axis and retain approximately every fourth step-final observation plus the endpoint; the full 1000 records remain in each CSV. All tick directions point inward and the background grid is disabled. Panel-bound checks are written to plot_QA.json; these are layout checks, not scientific validation. An example of each replot and its layout report are included in `examples/replotted/`.
