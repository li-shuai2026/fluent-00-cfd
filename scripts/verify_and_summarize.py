"""Recompute manuscript statistics and validate native checkpoint counts. No solver is used."""
from pathlib import Path
import argparse, csv, hashlib, json, math, statistics
ROOT = Path(__file__).resolve().parents[1]
def rows(path):
    with (ROOT/path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
def vals(rs,c): return [float(r[c]) for r in rs]
def trapmean(rs,c):
    ts=vals(rs,"flow_time_s");vs=vals(rs,c)
    return sum((b-a)*(x+y)/2 for a,b,x,y in zip(ts,ts[1:],vs,vs[1:]))/(ts[-1]-ts[0])
def save(out,name,rs):
    with (out/name).open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rs[0]));w.writeheader();w.writerows(rs)
def analyze(out):
    out.mkdir(parents=True,exist_ok=True)
    result={"description":"Recomputed from packaged native source rows; no interpolation or smoothing", "checks":[]}
    gridrows=[]
    for grid in ["coarse","medium","fine"]:
        rs=rows(f"data/three_grid/{grid}/monitor.csv")
        assert len(rs)==40
        ts=vals(rs,"flow_time_s")
        assert abs(ts[0]-150.25)<1e-6 and abs(ts[-1]-160)<1e-6
        assert all(abs(b-a-.25)<1e-6 for a,b in zip(ts,ts[1:]))
        for r in rs:
            a,b=abs(float(r["qin_m3_s"])),abs(float(r["qout_m3_s"]))
            assert math.isclose(100*abs(a-b)/a,float(r["mass_difference_pct"]),abs_tol=1e-7)
        for lab,group in [("150.25-155.00",rs[:20]),("155.25-160.00",rs[20:]),("150.25-160.00",rs)]:
            q=[abs(x) for x in vals(group,"qout_m3_s")];dq=vals(group,"mass_difference_pct")
            gridrows.append(dict(grid=grid,window_s=lab,n=len(group),mean_qout_m3_s=statistics.mean(q),mean_deltaQ_pct=statistics.mean(dq),max_deltaQ_pct=max(dq)))
        final=rows(f"data/three_grid/{grid}/residuals_final_iteration.csv")
        assert len(final)==1000
        assert abs(float(final[-1]["physical_time_s"])-160)<1e-6
    save(out,"table_3_3_grid.csv",gridrows);result["three_grid"]=gridrows
    all_dt=rows("data/time_step/exact_section_corrected.csv");dtrows=[]
    for dt,n,q,h in [(0.01,40,.686964,.721031),(.005,79,.687329,.721431),(.0025,157,.687553,.721702)]:
        rs=sorted([r for r in all_dt if math.isclose(float(r["dt_s"]),dt) and 150.25-1e-6<=float(r["flow_time_s"])<=160+1e-6],key=lambda r:float(r["flow_time_s"]))
        assert len(rs)==n,(dt,len(rs))
        qm=trapmean(rs,"qout_m3_s");hm=trapmean(rs,"mid_h_D")
        assert abs(qm-q)<.00000051 and abs(hm-h)<.00000051
        dtrows.append(dict(dt_s=dt,n=n,mean_qout_m3_s=qm,mean_mid_H_D=hm,mean_deltaQ_pct=trapmean(rs,"flow_difference_pct"),max_deltaQ_pct=max(vals(rs,"flow_difference_pct"))))
    save(out,"table_3_2_timestep.csv",dtrows);result["time_step"]=dtrows
    rs=rows("data/dense_coarse/monitor_200.csv");assert len(rs)==200
    ts=vals(rs,"flow_time_s");assert abs(ts[0]-150.05)<1e-6 and abs(ts[-1]-160)<1e-6
    assert all(abs(b-a-.05)<1e-6 for a,b in zip(ts,ts[1:]))
    dense={"n":len(rs),"t_start_s":ts[0],"t_end_s":ts[-1]}
    for c in ["qout_m3_s","mid_h_D","outlet_h_D","water_volume_m3","flow_difference_pct"]:
        vs=vals(rs,c);dense[c]={"mean":statistics.mean(vs),"min":min(vs),"max":max(vs),"end_minus_start":vs[-1]-vs[0]}
    dense["qout_cv_pct"]=100*statistics.pstdev(vals(rs,"qout_m3_s"))/statistics.mean(vals(rs,"qout_m3_s"))
    dense["mid_depth_range_mm"]=1000*(max(vals(rs,"mid_depth_m"))-min(vals(rs,"mid_depth_m")))
    result["dense_coarse"]=dense
    bc=rows("data/boundary/monitor.csv");bcrows=[]
    for condition in sorted(set(r["condition_id"] for r in bc)):
        group=[r for r in bc if r["condition_id"]==condition];assert len(group)==40
        bcrows.append(dict(condition=condition,n=len(group),mean_qout_m3_s=statistics.mean(vals(group,"qout_m3_s")),mean_mid_H_D=statistics.mean(vals(group,"mid_h_D")),mean_outlet_H_D=statistics.mean(vals(group,"outlet_h_D"))))
    save(out,"boundary_means.csv",bcrows);result["boundary"]=bcrows
    rough=rows("data/roughness/manning_sweep.csv");assert len(rough)==14641
    C=(.786/.8)**(8/3)
    for row in rough:
        a,b=float(row["n1"]),float(row["n2"])
        assert math.isclose(float(row["K"]),C*a/b,abs_tol=1e-9)
        assert math.isclose(float(row["eta"]),C*.013/b,abs_tol=1e-9)
    result["roughness"]={"n":len(rough),"C":C,"K_min":min(vals(rough,"K")),"K_max":max(vals(rough,"K")),"n2_design_threshold":C*.013}
    result["checks"]=["three grids x40 native monitor points", "three grids x1000 final-iteration residual records", "200 dense coarse checkpoints", "40/79/157 common-window timestep samples", "3x40 boundary samples", "14641 Manning sweep combinations", "recorded instantaneous flow difference formula"]
    (out/"summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print("PASS: native counts, formulas and published timestep statistics. Output:",out)
def verify():
    manifest=rows("metadata/SHA256SUMS.csv")
    for row in manifest:
        p=ROOT/row["path"];h=hashlib.sha256()
        with p.open("rb") as f:
            for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
        assert p.stat().st_size==int(row["bytes"]) and h.hexdigest()==row["sha256"],p
    print("PASS:",len(manifest),"SHA-256 checksums")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--verify-files",action="store_true");p.add_argument("--output",type=Path,default=ROOT/"reproduced/statistics");a=p.parse_args()
    if a.verify_files:verify()
    analyze(a.output)
