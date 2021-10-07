#!/usr/bin/env python3
import lib
from lib.common import group, calc_stat
from collections import OrderedDict

g = group(lib.get_runs(["ctl_baselines_rnn"]), ["ctl.reversed", "seq_classifier.rnn"])
g.update(group(lib.get_runs(["ctl_baselines_transformer_11"], {"config.state_size": 128}), ["ctl.reversed", "transformer.variant"]))
g.update({k+"_noabs": v for k, v in group(lib.get_runs(["ctl_tcf_no_absgate"]), ["ctl.reversed", "transformer.variant"]).items()})
g.update({k+"_abs": v for k, v in group(lib.get_runs(["ctl_tcf"]), ["ctl.reversed", "transformer.variant"]).items()})
g.update(group(lib.get_runs(["ctl_tcf_geometric"]), ["ctl.reversed", "transformer.variant"]))
g.update(group(lib.get_runs(["ctl_baselines_transformer_geometric"]), ["ctl.reversed", "transformer.variant"]))
print(g.keys())

highlight_threshold = 0.025

IID_KEY = "validation/valid/accuracy/iid"
GEN_KEY = "validation/test/accuracy/deeper"
VAL_KEY = "validation/valid/accuracy/deeper_val"

model_list = OrderedDict()
model_list["seq_classifier.rnn_lstm"] = "LSTM"
model_list["seq_classifier.rnn_dnc"] = "DNC"
model_list["asd"] = None
model_list["transformer.variant_universal"] = "Transformer"
model_list["transformer.variant_relative_universal"] = "\quad + rel"
model_list["transformer.variant_tcf_residual_noabs"] = "\quad + rel + gate"
model_list["transformer.variant_tcf_residual_abs"] = "\quad + abs/rel + gate"
model_list["transformer.variant_geometric_transformer"] = "\quad + geom. att."
model_list["transformer.variant_tcf_geometric"] = "\quad + geom. att. + gate (TCF)"


siid = calc_stat(g, lambda k: k in {IID_KEY})
sgen = lib.CrossValidatedStats(GEN_KEY, VAL_KEY)(g)

def format_res(r):
    # r = r.get()
    return f"{r.mean:.2f} $\\pm$ {r.std:.2f}"

print("Model & IID -> & IID <- & Longer -> & Longer <- \\\\")
print("\\midrule")
rows = []
for k, name in model_list.items():
    if name is None:
        rows.append(None)
        continue
    line = []
    for r in [1, 0]:
        sthis = siid[f"ctl.reversed_{r}/{k}"]

        line.append(sthis[IID_KEY].get())

    for r in [1, 0]:
        sthis = sgen[f"ctl.reversed_{r}/{k}"]

        line.append(sthis)

    rows.append(line)

maxcol = [max([r[c].mean for r in rows if r]) for c in range(len(rows[0]))]

for name, line in zip(model_list.values(), rows):
    if line is None:
        print("\\midrule")
        continue

    fline = [format_res(c) for ci, c in enumerate(line)]
    fline = [f"\\bf{{{fc}}}" if (maxcol[ci] - line[ci].mean) < highlight_threshold else fc for ci, fc in enumerate(fline)]
    print(name+" & " + " & ".join(fline) + " \\\\")

print("\\bottomrule")