# Computational execution record

The statistical protocol was frozen before prior simulation and outcome fitting. Two four-worker launches failed before producing a trace; the matching macOS crash report identified a child-side fork crash during matrix multiplication. Switching to spawn resolved launch failures. A subsequent default, uncompiled PyTensor run was interrupted after a benchmark measured roughly 0.23–0.40 seconds per gradient evaluation. No completed posterior was inspected from these runs.

The same PyMC model and PyMC NUTS sampler were then configured with PyTensor's documented NUMBA compilation mode. At the model initial point, the compiled gradient agreed with the Python reference at rtol=atol=1e-8, and execution took about 0.0005 seconds per evaluation. This changes computation, not likelihood, priors, exposure, formula, chain count, seed, tuning, draws or target acceptance. The interrupted and failed attempts remain archived separately. Additional dependencies are pinned in the isolated Stage 3C environment. No prior-stage environment was modified.

Documentation: https://pytensor.readthedocs.io/en/latest/library/compile/mode.html
