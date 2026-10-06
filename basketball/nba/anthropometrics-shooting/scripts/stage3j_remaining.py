"""Complete independent declared sensitivities when J2 numerical gate is unresolved.
Executes the exact AST suffix of the hash-guarded original driver; no new estimator.
"""
from stage3j_core import *
from stage3j_run import diagnostics
import ast
p=authorize(True);d=load()
assert not (E/'j3_first_season_result.json').exists()
source=ROOT/'scripts/stage3j_run.py';tree=ast.parse(source.read_text())
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='sensitivities')
start=next(i for i,n in enumerate(function.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='first' for t in n.targets))
body=ast.Module(body=function.body[start:],type_ignores=[])
save('remaining_sensitivities_execution.json',dict(started_at=now(),reason='Execute independent predeclared secondary analyses while J2 bootstrap numerical failures are retained; no J2 interval interpretation or repair',source_sha256=sha(source),exact_original_AST_suffix_sha256=hashlib.sha256(ast.dump(body).encode()).hexdigest(),primary_sha256=sha(E/'primary_result.json'),model_changes=False),True)
exec(compile(ast.fix_missing_locations(body),str(source),'exec'))
