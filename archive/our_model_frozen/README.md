# Frozen — the parallel model track

Superseded by the corrected `Model2_ori.py` at the repository root. Kept for the
audit trail and because the analysis behind the input data lives in `pipeline/`
and is still live.

`Model3.py` = `Model2.py` + a 25% per-country cap (US exempt: the 60% region cap
over two regions forces US ≥ 40%, so a lower cap on the US is infeasible).
`Model4.py` = `Model2.py` + Chloe's 30% sector cap and her controversial screen,
with the ticker and tag fixes.

Both assert that they reproduce `Model2.py` exactly when their additions are
disabled — `0.00e+00` on return, risk and every weight.

`FROZEN_v3_*` is the country-cap freeze; `FROZEN_v4_*` the sector-cap one.
`FINAL_*` and `FROZEN_*` are earlier generations, in that order.

The one finding here that the current model does not carry: the country cap and
the sector cap do **not** overlap. With only the country cap, sector exposure
rises to 39.8%; with only the sector cap, Switzerland rises to 46.8%. Blocking
one concentration channel pushes exposure into the other.
