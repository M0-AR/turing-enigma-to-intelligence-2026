"""Benchmarks: timing + hidden-pattern measurements for the paper.

- TM steps/s, BB5 rate estimate
- Enigma throughput, Bombe contradiction depth (avg deductions before reject)
- Banburismus accuracy vs length (synthetic English at match rate m)
- RL learning curve (win rate @ 0/100/1k/10k games)
- Pattern variance vs diffusion ratio sweep
Writes results/benchmark.json
"""
import sys, time, json, random, math
sys.path.insert(0, "src")
from turing_universe.turing_machine import TuringMachine, binary_increment_table, run_blank, beaver_table_5state_champion
from turing_universe.enigma import EnigmaMachine
from turing_universe.bombe import follow
from turing_universe.banburismus import score_pair
from turing_universe.learning import SticksChild
from turing_universe.morphogenesis import run_pattern, pattern_stats

res = {}
t0=time.time(); tm=TuringMachine(binary_increment_table())
for _ in range(2000): tm.run("1011")
res["tm_add1_per_s"] = 2000/(time.time()-t0)

t0=time.time(); st,h,_=run_blank(beaver_table_5state_champion(),"A",300_000)
res["bb5_steps_per_s"] = 300_000/(time.time()-t0)
res["bb5_full_47M_est_s"] = 47_176_870/res["bb5_steps_per_s"]

t0=time.time(); e=EnigmaMachine(["IV","II","V"],["A","A","A"],["K","D","F"],{},"B")
e.encrypt("A"*20000)
res["enigma_letters_per_s"] = 20000/(time.time()-t0)

# Bombe: avg deductions — measure survivors tested on 200 wrong settings
menu=[("W","V",0),("E","Q",1),("A","X",2),("T","K",3),("H","M",4),("E","N",5)]
wrong=0; t0=time.time()
for n in range(200):
    s=[chr(65+(n//676)%26),chr(65+(n//26)%26),chr(65+n%26)]
    r=follow(menu,["I","II","III"],s,seed_guess=(menu[0][0],"X"))
    if r is None: wrong+=1
res["bombe_reject_rate_200"] = wrong/200
res["bombe_time_200_s"] = time.time()-t0

# Banburismus: synthetic accuracy vs length
def trial(L, m_same=0.065, trials=400):
    import random as R
    rng=R.Random(0); ok=0
    for _ in range(trials):
        same = rng.random()<0.5
        rate = m_same if same else 1/26
        matches=sum(1 for _ in range(L) if rng.random()<rate)
        # score with empirical weights from m_same
        pm=10*math.log10(m_same*26); pmm=10*math.log10((1-m_same)*26/25)
        sc=matches*pm+(L-matches)*pmm
        if (sc>0)==same: ok+=1
    return ok/trials
for L in [100,400,1700]:
    res[f"banburismus_acc_{L}"] = trial(L)

# RL curve
for g in [0,100,1000,10000]:
    c=SticksChild(seed=2); c.train(g)
    res[f"rl_win_vs_expert_{g}"] = c.win_rate_vs_expert(500)

# Pattern sweep
for ratio in [1,6,18]:
    U=run_pattern(48,48,800,Du=0.16,Dv=0.16*ratio,seed=0)
    s=pattern_stats(U)
    res[f"pattern_var_ratio_{ratio}"]=s["var"]; res[f"pattern_peaks_ratio_{ratio}"]=s["peaks"]

print(json.dumps(res, indent=2))
open("results/benchmark.json","w").write(json.dumps(res, indent=2))
