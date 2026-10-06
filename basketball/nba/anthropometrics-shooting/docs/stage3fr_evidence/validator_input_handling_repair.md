# Equivalence validator input handling repair

R2's first validation invocation stopped with a Python TypeError before any equivalence decision or posterior fit. In centered coordinates, the observed likelihood does not directly depend on covariance coordinates; PyMC's default likelihood compiler omitted these inputs, whereas the validator supplied the full matched parameter point.

The unfrozen validator now explicitly compiles the same observed log likelihood with all model value variables and permits unused inputs. This changes only the callable input interface, not its mathematical value. The frozen model, priors, transformations, Jacobian treatment, seeds, and tolerances were unchanged. The original error log is preserved as `r2_equivalence_input_error.txt`.

The corrected R2 validation passed all checks. R1's completed validation was preserved and not repeated. This was a validator implementation error, not an equivalence failure or a sampler recovery.
