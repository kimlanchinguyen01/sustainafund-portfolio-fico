"""Перевірка ліцензії Xpress: розв'язує крихітну MIQP-задачу."""
import os
os.environ['XPAUTH_PATH'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'xpauth.xpr'))
import xpress as xp

print("Xpress version:", xp.getVersion())

# міні-портфель: 3 активи, квадратична ціль + бінарний вибір
p = xp.problem()
w = [p.addVariable(lb=0, ub=0.6, name=f"w{i}") for i in range(3)]
b = [p.addVariable(vartype=xp.binary, name=f"b{i}") for i in range(3)]
mu = [0.10, 0.14, 0.08]
p.addConstraint(xp.Sum(w) == 1)
p.addConstraint(b[i] * 0.05 <= w[i] for i in range(3))   # min 5% якщо обрано
p.addConstraint(w[i] <= b[i] for i in range(3))          # звʼязок w<->b
p.addConstraint(xp.Sum(b) >= 2)                          # мінімум 2 активи
risk = xp.Sum(w[i] * w[i] for i in range(3))             # квадратичний член
p.setObjective(risk - 2 * xp.Sum(mu[i] * w[i] for i in range(3)), sense=xp.minimize)
p.controls.outputlog = 0
p.optimize()

print("status:", p.attributes.solvestatus, "/", p.attributes.solstatus)
print("ваги:", [round(v, 4) for v in p.getSolution(w)])
print("обрано:", [round(v) for v in p.getSolution(b)])
print("\n✅ Ліцензія працює, MIQP розвʼязується.")
