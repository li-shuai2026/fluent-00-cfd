"""Replot the six source-data comparisons; do not overwrite manuscript exports.

Matplotlib only; native observations, no smoothing. Layout is reproducible but
does not claim pixel identity with the historically edited manuscript images.
"""
from pathlib import Path
import argparse
import csv
import json
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator

ROOT = Path(__file__).resolve().parents[1]
COLORS = ['#0072B2', '#D55E00', '#009E73']
def read(p):
    with (ROOT/p).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
def values(rows, key):
    return [float(r[key]) if r.get(key, '') else math.nan for r in rows]
def draw(ax, rows, key, label=None, color=COLORS[0], every=1, absolute=False):
    # Keep the last observation when thinning the residual display.
    ix=list(range(0,len(rows),every))
    if ix[-1] != len(rows)-1:
        ix.append(len(rows)-1)
    group=[rows[i] for i in ix]
    t='flow_time_s' if 'flow_time_s' in group[0] else 'physical_time_s'
    y=values(group,key)
    if absolute: y=[abs(v) for v in y]
    ax.plot(values(group,t),y,label=label,color=color,lw=0.95)
def panels(n=4):
    fig, axes=plt.subplots(2,2,figsize=(7.2,5.5),layout='constrained') if n==4 else plt.subplots(1,2,figsize=(7.2,2.9),layout='constrained')
    axes=list(axes.flat)
    for letter,ax in zip('abcd',axes):
        ax.text(0,1.035,f'({letter})',transform=ax.transAxes,fontweight='bold',va='bottom')
        ax.set_xlabel(r'$t$ (s)')
    return fig,axes

def save(fig, number, out, qa):
    for ax in fig.axes:
        ax.grid(False)
        ax.tick_params(which='both',direction='in',top=True,right=True)
        ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        if ax.get_yscale()=='linear': ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        ax.tick_params(which='major',length=4,width=.7)
        ax.tick_params(which='minor',length=2,width=.6)
        if ax.get_legend_handles_labels()[0]:
            ax.legend(frameon=False,fontsize=7,loc='best')
    fig.canvas.draw()
    # Check panel placement after constrained layout. Tick labels remain inward.
    renderer=fig.canvas.get_renderer()
    boxes=[ax.get_tightbbox(renderer) for ax in fig.axes]
    overlaps=[]
    for i,a in enumerate(boxes):
        for j,b in enumerate(boxes[i+1:],i+1):
            if a.overlaps(b): overlaps.append([i,j])
    qa.append({'figure':number,'axes':len(fig.axes),'overlapping_panel_bounds':overlaps})
    for suffix in ['png','pdf','svg']:
        fig.savefig(out/f'Figure_3_{number}_replotted.{suffix}',dpi=400)
    plt.close(fig)

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.labelsize':9,
                         'axes.linewidth':.7,'svg.fonttype':'none','pdf.fonttype':42})
    qa=[]
    rs=read('data/baseline/baseline_monitor.csv')
    fig,axes=panels()
    for ax,key,label in zip(axes[:2],['outlet_Q_m3_s','mid_h_D'],[r'$Q_{\mathrm{out}}$ (m$^3$ s$^{-1}$)',r'$H_{\mathrm{mid}}/D$']):
        draw(ax,rs,key);ax.set_ylabel(label)
    p=read('data/baseline/axial_layer_profile_150s.csv')
    axes[2].plot(values(p,'x_m'),values(p,'h_D'),color=COLORS[0],lw=.95)
    axes[2].set(xlabel=r'$x$ (m)',ylabel=r'$H/D$')
    draw(axes[3],rs,'absolute_flow_difference_pct');axes[3].set_ylabel(r'$\delta_Q$ (%)')
    save(fig,1,out,qa)

    rs=read('data/dense_coarse/monitor_200.csv');fig,axes=panels()
    for ax,key,label in zip(axes,['qout_m3_s','mid_h_D','water_volume_m3','flow_difference_pct'],
            [r'$Q_{\mathrm{out}}$ (m$^3$ s$^{-1}$)',r'$H_{\mathrm{mid}}/D$',r'$V_{\mathrm{w}}$ (m$^3$)',r'$\delta_Q$ (%)']):
        draw(ax,rs,key);ax.set_ylabel(label)
    axes[0].axhline(.687,color='0.4',lw=.8,ls='--',label=r'$Q_{\mathrm{in}}$')
    save(fig,2,out,qa)

    rs=read('data/time_step/exact_section_corrected.csv');fig,axes=panels()
    for dt,c in zip([.01,.005,.0025],COLORS):
        group=sorted([r for r in rs if float(r['dt_s'])==dt and float(r['flow_time_s'])>=150.25-1e-7],key=lambda r:float(r['flow_time_s']))
        for ax,key in zip(axes,['qout_m3_s','mid_h_D','flow_difference_pct','mid_h_D_delta_from_start']):
            draw(ax,group,key,fr'$\Delta t={dt:g}$ s',c)
    for ax,label in zip(axes,[r'$Q_{\mathrm{out}}$ (m$^3$ s$^{-1}$)',r'$H_{\mathrm{mid}}/D$',r'$\delta_Q$ (%)',r'$\Delta(H_{\mathrm{mid}}/D)$']): ax.set_ylabel(label)
    save(fig,3,out,qa)

    fig,axes=panels()
    for grid,c in zip(['coarse','medium','fine'],COLORS):
        rs=read(f'data/three_grid/{grid}/monitor.csv')
        draw(axes[0],rs,'qout_m3_s',grid,c,absolute=True)
        draw(axes[1],rs,'mass_difference_pct',grid,c)
        rr=read(f'data/three_grid/{grid}/residuals_final_iteration.csv')
        draw(axes[2],rr,'continuity',grid,c,every=4)
        draw(axes[3],rr,'epsilon',grid,c,every=4)
    for ax,label in zip(axes,[r'$Q_{\mathrm{out}}$ (m$^3$ s$^{-1}$)',r'$\delta_Q$ (%)','Continuity residual',r'$\varepsilon$ residual']): ax.set_ylabel(label)
    axes[2].set_yscale('log');axes[3].set_yscale('log')
    save(fig,4,out,qa)

    rs=read('data/boundary/monitor.csv');fig,axes=panels()
    for condition,c in zip(sorted({r['condition_id'] for r in rs}),COLORS):
        group=[r for r in rs if r['condition_id']==condition]
        for ax,key in zip(axes,['qout_m3_s','mid_h_D','outlet_h_D','flow_difference_pct']): draw(ax,group,key,group[0]['condition_en'],c)
    for ax,label in zip(axes,[r'$Q_{\mathrm{out}}$ (m$^3$ s$^{-1}$)',r'$H_{\mathrm{mid}}/D$',r'$H_{\mathrm{out}}/D$',r'$\delta_Q$ (%)']): ax.set_ylabel(label)
    save(fig,5,out,qa)

    rs=read('data/roughness/manning_sweep.csv');fig,axes=panels(2)
    import matplotlib.tri as tri
    x=values(rs,'n1');y=values(rs,'n2');mesh=tri.Triangulation(x,y)
    for ax,key in zip(axes,['K','eta']):
        artist=ax.tricontourf(mesh,values(rs,key),levels=16,cmap='viridis')
        ax.set(xlabel=r'$n_1$ (s m$^{-1/3}$)',ylabel=r'$n_2$ (s m$^{-1/3}$)')
        cb=fig.colorbar(artist,ax=ax,pad=.025,shrink=.88)
        cb.set_label(r'$K$' if key=='K' else r'$\eta$')
    save(fig,6,out,qa)
    (out/'plot_QA.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
    print('REPLotted six source comparisons:',out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=ROOT/'reproduced/figures')
    main(p.parse_args().output)
