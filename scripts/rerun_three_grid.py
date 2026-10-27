"""Run coarse, medium and fine grid continuations from the common 150 s state.

Each grid is run serially for 10 s of physical time with dt=0.01 s and at
most 30 inner iterations per time step.  Medium and fine grids are obtained
by Fluent mesh replacement with solution interpolation enabled, starting from
the same 150 s coarse-grid case/data pair.
"""
from pathlib import Path
import csv
import json
import math
import os
import time
import traceback

import argparse
import sys
pf = None

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "models/baseline_150s/coarse_150s.cas.h5"
SOURCE_DATA = ROOT / "models/baseline_150s/coarse_150s.dat.h5"
OUT = ROOT / "reruns/three_grid"
DT, STEPS, INNER, PROCESSORS, CHECKPOINT_STEPS = 0.01, 1000, 30, 14, 25
FLUENT_PATH = None
GRIDS = [("coarse", None, 225000),
         ("medium", ROOT / "models/mesh/medium.msh", 450000),
         ("fine", ROOT / "models/mesh/fine.msh", 900000)]



def log(message):
    line = time.strftime("%Y-%m-%d %H:%M:%S ") + message
    with (OUT / "three_grid_run.log").open("a", encoding="utf-8") as stream:
        stream.write(line + "\n")
    print(line, flush=True)


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def make_reports(session, prefix):
    surface = session.settings.solution.report_definitions.surface
    names = []
    for name, state in [
        (f"{prefix}_qin", {"report_type": "surface-volumeflowrate", "phase": "phase-2", "surface_names": ["inlet-water"]}),
        (f"{prefix}_qout", {"report_type": "surface-volumeflowrate", "phase": "phase-2", "surface_names": ["outlet-single"]}),
    ]:
        try:
            surface.delete(name)
        except Exception:
            pass
        surface.create(name)
        surface[name].set_state(state)
        names.append(name)
    return names


def report_values(session, names):
    values = {}
    for result in session.settings.solution.report_definitions.compute(report_defs=names):
        for key, value in result.items():
            values[key] = float(value[0] if isinstance(value, (list, tuple)) else value)
    return values


def run_grid(name, mesh, cells):
    root = OUT / name
    root.mkdir(parents=True, exist_ok=True)
    case_out = root / f"{name}_rerun_final.cas.h5"
    csv_path = root / "monitor.csv"
    log(f"{name.upper()}_LAUNCH cells={cells} mesh={mesh or 'source mesh'}")
    session = None
    try:
        session = pf.launch_fluent(
            product_version="26.1.0", dimension=3, precision="double",
            processor_count=PROCESSORS, mode="solver", ui_mode="no_gui",
            **({"fluent_path": FLUENT_PATH} if FLUENT_PATH else {}),
            start_timeout=300, cleanup_on_exit=False,
        )
        session.transcript.start(file_name=str(root / f"{name}.trn"))
        session.settings.file.read_case(file_name=str(SOURCE))
        session.settings.file.read_data(file_name=str(SOURCE_DATA))
        loaded_time = float(session.scheme.eval("(rpgetvar 'flow-time)"))
        loaded_step = int(session.scheme.eval("(rpgetvar 'time-step)"))
        if abs(loaded_time - 150.0) > 1e-7:
            raise RuntimeError(f"{name}: source time is {loaded_time}, expected 150 s")

        if mesh is not None:
            # Fluent's mesh replacement command interpolates the loaded 150 s
            # solution across the new cell zones when zones=True.
            session.settings.mesh.replace(file_name=str(mesh), zones=True)
            session.settings.mesh.check()
            session.settings.mesh.quality()
            session.settings.mesh.size_info()
            log(f"{name.upper()}_MESH_REPLACED solution_interpolated=True")

        after_mesh_time = float(session.scheme.eval("(rpgetvar 'flow-time)"))
        if abs(after_mesh_time - 150.0) > 1e-7:
            raise RuntimeError(f"{name}: mesh replacement changed flow time to {after_mesh_time}")

        reports = make_reports(session, name)
        run = session.settings.solution.run_calculation
        run.parameters.time_step_size = DT
        run.parameters.max_iter_per_time_step = INNER
        run.parameters.reporting_interval = 1
        write_json(root / "setup.json", {
            "grid": name, "cells_expected": cells,
            "mesh": str(mesh) if mesh else "source mesh",
            "source_case": str(SOURCE), "source_data": str(SOURCE_DATA),
            "source_flow_time_s": loaded_time, "source_fluent_step": loaded_step,
            "duration_s": STEPS * DT, "time_step_s": DT, "steps": STEPS,
            "max_iter_per_time_step": INNER, "processors": PROCESSORS,
            "mesh_solution_transfer": "Fluent mesh.replace(zones=True)",
        })

        with csv_path.open("w", newline="", encoding="utf-8-sig") as stream:
            writer = csv.writer(stream)
            writer.writerow(["step", "flow_time_s", "qin_m3_s", "qout_m3_s", "mass_difference_pct", "elapsed_s"])
            completed = 0
            while completed < STEPS:
                # Record exactly at 25, 50, 75, ... time steps.
                count = min(CHECKPOINT_STEPS, STEPS - completed)
                started = time.time()
                run.parameters.time_step_count = count
                run.calculate()
                elapsed = time.time() - started
                step = int(session.scheme.eval("(rpgetvar 'time-step)"))
                flow_time = float(session.scheme.eval("(rpgetvar 'flow-time)"))
                expected_step = loaded_step + completed + count
                expected_time = 150.0 + (completed + count) * DT
                if step != expected_step or abs(flow_time - expected_time) > 1e-7:
                    raise RuntimeError(
                        f"{name}: stopped at step={step}, time={flow_time}; "
                        f"expected {expected_step}, {expected_time}"
                    )
                values = report_values(session, reports)
                qin = values[reports[0]]
                qout = values[reports[1]]
                imbalance = abs(abs(qin) - abs(qout)) / max(abs(qin), 1e-30) * 100.0
                if not all(math.isfinite(v) for v in (qin, qout, imbalance)):
                    raise RuntimeError(f"{name}: non-finite monitor result")
                completed += count
                writer.writerow([completed, flow_time, qin, qout, imbalance, elapsed])
                stream.flush()
                stem = root / f"{name}_step_{completed:05d}.cas.h5"
                session.settings.file.write_case_data(file_name=str(stem))
                log(
                    f"{name.upper()}_CHECKPOINT steps={completed}/{STEPS} "
                    f"time={flow_time:.3f} qin={qin:.9f} qout={qout:.9f} "
                    f"imbalance={imbalance:.5f}% elapsed={elapsed:.1f}s"
                )

            final_time = float(session.scheme.eval("(rpgetvar 'flow-time)"))
            if abs(final_time - (150.0 + STEPS * DT)) > 1e-7:
                raise RuntimeError(f"{name}: final time {final_time}, expected {150.0 + STEPS * DT}")
            session.settings.file.write_case_data(file_name=str(case_out))

        write_json(root / "complete.json", {
            "status": "complete", "grid": name, "source_time_s": 150.0,
            "target_time_s": 150.0 + STEPS * DT, "steps": STEPS, "dt_s": DT,
            "max_iter_per_time_step": INNER, "case": str(case_out),
        })
        log(f"{name.upper()}_COMPLETE time={final_time:.6f} case={case_out}")
    finally:
        if session is not None:
            try:
                session.transcript.stop()
            except Exception:
                pass
            try:
                session.exit()
            except Exception:
                pass


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    if not SOURCE.exists() or not SOURCE_DATA.exists():
        raise FileNotFoundError("150 s source case/data pair is incomplete")
    for name, mesh, cells in GRIDS:
        if mesh is not None and not mesh.exists():
            raise FileNotFoundError(mesh)
    write_json(OUT / "run_config.json", {
        "source_case": str(SOURCE), "source_data": str(SOURCE_DATA),
        "start_time_s": 150.0, "duration_s": STEPS * DT, "target_time_s": 150.0 + STEPS * DT,
        "dt_s": DT, "steps": STEPS, "max_iter_per_time_step": INNER,
        "processors": PROCESSORS,
        "order": [name for name, _, _ in GRIDS],
    })
    log(f"SEQUENTIAL_RUN_START dt={DT} inner={INNER} duration={STEPS * DT}s order={','.join(g[0] for g in GRIDS)}")
    for name, mesh, cells in GRIDS:
        run_grid(name, mesh, cells)
    log("SEQUENTIAL_RUN_COMPLETE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Portable three-grid Fluent rerun; default is dry-run.")
    parser.add_argument("--execute", action="store_true", help="Launch Fluent and consume a solver license")
    parser.add_argument("--grid", choices=["all", "coarse", "medium", "fine"], default="all")
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--processors", type=int, default=14)
    parser.add_argument("--fluent-path", help="Optional local Fluent executable")
    parser.add_argument("--smoke-steps", type=int, help="Run only this many steps instead of 1000")
    args = parser.parse_args()
    if args.processors < 1 or (args.smoke_steps is not None and not 1 <= args.smoke_steps <= 1000):
        parser.error("processors >= 1 and smoke-steps in 1..1000 are required")
    if args.grid != "all":
        GRIDS = [g for g in GRIDS if g[0] == args.grid]
    OUT, PROCESSORS, FLUENT_PATH = args.output.resolve(), args.processors, args.fluent_path
    if args.smoke_steps is not None:
        STEPS = args.smoke_steps
    expected_target = 150 + STEPS * DT
    for f in [SOURCE, SOURCE_DATA] + [g[1] for g in GRIDS if g[1] is not None]:
        if not f.exists():
            raise FileNotFoundError(f)
    print(json.dumps({"launch": args.execute, "grids": [g[0] for g in GRIDS],
                      "start_s": 150, "target_s": expected_target, "dt_s": DT,
                      "max_inner_iterations": INNER, "checkpoints_every_steps": CHECKPOINT_STEPS,
                      "processors": PROCESSORS, "output": str(OUT)}, indent=2))
    if not args.execute:
        print("Dry-run only. Add --execute to launch Fluent. No solver has been launched.")
        sys.exit(0)
    if OUT.exists() and any(OUT.iterdir()):
        raise FileExistsError("Choose a new empty output directory; reruns do not overwrite existing output")
    # Explicit command-line execution is required before importing/launching the solver.
    import ansys.fluent.core as pf
    main()
