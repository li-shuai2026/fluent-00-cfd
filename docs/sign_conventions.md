# Signs, definitions and sampling

- Native three-grid `monitor.csv` keeps positive inlet flow and negative outlet flow as returned by the archived reports. Processed comparison files generally use positive outlet-flow magnitude. Check the CSV column and source before plotting.
- The native `mass_difference_pct` label is preserved for traceability. Its implemented formula is 100*abs(abs(Qin)-abs(Qout))/abs(Qin); describe it as instantaneous inlet/outlet water-flow difference, rather than a proven global conservation error.
- Water flow has units m3/s. Mixture mass flow in kg/s must not be compared directly with water-phase volume flow without density and phase accounting.
- H/D is an area-equivalent water depth divided by D=0.786 m, obtained by inverting the wetted circular-segment area. A volume fraction, a cross-sectional area fraction and H/D are different quantities.
- `axial_layer_profile_150s.csv` uses finite axial layers; a layer average and an exact x-section can differ. The corrected timestep dataset explicitly uses exact-section extraction at the midpoint.
- Three-grid monitors: 40 points each, 150.25–160 s, spacing 0.25 s. Residual-final files: 1000 points each, 150.01–160 s. Dense coarse: 200 points, 150.05–160 s, spacing 0.05 s. The initial 150 s field is supplied separately.
- A smooth line joins actual saved observations; it does not create a new solved checkpoint. Marker thinning changes display only.
- Residuals are scaled solver residuals. Temporal stability of monitors, inner-iteration residuals and transient storage balance are separate diagnostics.
