# Model and numerical settings

The saved model files are authoritative for the properties inspected here. `metadata/saved_state_audit.json` records values extracted directly from case/data HDF5 datasets; this is an audit of saved files, not a new solver execution.

| Item | Saved setting |
| --- | --- |
| Software | ANSYS Fluent 2026 R1 / file version 26.1, 3D double precision |
| Pipe | Length 30 m; internal diameter 0.786 m |
| Mesh cells | Coarse 225000, medium 450000, fine 900000 |
| Multiphase | Transient air–water VOF |
| Turbulence | Realizable k–epsilon; standard wall functions |
| Pressure/velocity | PISO; PRESTO! pressure interpolation |
| Interface | Geo-Reconstruct |
| Momentum/turbulence | Second-order upwind |
| Time scheme | First-order implicit |
| Three-grid time window | Common 150 s state to 160 s |
| Timestep / inner iterations | 0.01 s / maximum 30 per step |
| Time-step comparison | 0.01, 0.005, 0.0025 s; maximum 30 iterations |
| Grid-monitor save interval | 25 steps = 0.25 s |
| Separate dense coarse run | 5 steps = 0.05 s; 200 observations |
| Inlet water velocity | 1.901743605170804 m/s; nominal water flow 0.687 m3/s |
| Inlet air velocity | 0.1 m/s |
| Wall sand-grain roughness | 0.00032 m; roughness constant 0.5 |
| Gravity in mesh coordinates | (0.024524923, -9.81, 0) m/s2 |
| Baseline outlet | Pressure outlet: free-surface elevation 0.0822 m; bottom elevation -0.468 m; specified depth 0.5502 m |

## Geometry and elevations

The supplied mesh is axis-aligned: x = 0–30 m, y and z bounds = +/-0.393 m. The axial gravity component represents the pipe slope, approximately 0.0025. Do not tilt this mesh a second time while retaining that gravity vector. The plotted engineering bed elevation is reconstructed as -0.393 - 0.0025*x m, giving -0.468 m at the outlet. An engineering elevation and a raw mesh y-coordinate must not be interchanged.

The outlet settings above are Fluent boundary inputs. An area-equivalent outlet H/D extracted from the computed VOF field is a separate reported quantity. The 0.70 reference is a capacity-comparison condition; it is not an imposed upper limit on every internal section.

## Mesh transfer

All three grid continuations start from the same coarse-grid 150 s case/data pair. The medium and fine cases use Fluent mesh replacement with solution transfer (`mesh.replace(..., zones=True)`), followed by mesh checks. They are not independent cold starts. No verified original CAD file or complete mesh-generation script has been recovered; the actual mesh files are supplied.

## Outlet scenarios

Low and high tailwater cases prescribe depths 0.5002 and 0.6002 m (same bottom elevation -0.468 m). The third scenario uses the Fluent **Outflow** boundary type. Historical phrases such as “free discharge” identify that numerical scenario; they do not establish an experimentally validated free-fall outlet.

## Roughness sweep

`data/roughness/manning_sweep.csv` is an analytical calculation using C=(0.786/0.8)^(8/3), K=C*n1/n2 and eta=C*0.013/n2. It is not a set of separately solved CFD roughness cases. Sand-grain roughness ks and Manning n are different parameters; do not equate them without the stated conversion assumptions.
