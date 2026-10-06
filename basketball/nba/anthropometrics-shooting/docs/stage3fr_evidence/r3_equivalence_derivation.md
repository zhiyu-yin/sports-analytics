# R3 exact mixed parameterization, predeclared before new fits

Order player effects as (u,v,h). Let L be the lower Cholesky factor under the unchanged 3-dimensional LKJ eta=2 covariance prior, and A=L[:2,:2]. Original coordinates are independent standard normal z=(z0,z1,z2), with r=Lz.

Forward: q=(u,v)=A(z0,z1); e=z2. Then h=L20*z0+L21*z1+L22*e.

Inverse: z0=u/L00; z1=(v-L10*z0)/L11; z2=e. Equivalently, from full r, e=(h-L20*z0-L21*z1)/L22. Positive Cholesky diagonals make this invertible almost surely.

New joint latent density: q~MVNormal(0,A*A.T), e~Normal(0,1), independently conditional on L. The forward Jacobian from z to (q,e) is det(A)=L00*L11 per player. Therefore log p(q,e|L) + log det(A) = log p(z). Across N players add N*log det(A). For covariance-dependent transformations the full Jacobian is block triangular with covariance coordinates unchanged, so this is still the complete determinant contribution. The MvNormal density includes this normalization; no additional Potential is added.

The induced r has covariance L*L.T, exactly the original distribution. The same deterministic r enters the same likelihood. R1 coefficient scaling remains, with independent theta_std priors having SD 0.5*s; its coordinate Jacobian is sB*sW. No covariance prior, scientific coefficient prior, categorical coding, predictor, outcome or conditioning set changes.

Accuracy and positive-count directions are centered, while the conditional hurdle residual is non-centered. This fixed choice reflects the likelihood structures (3980 positive accuracy/count rows and sparse binary failures), without fitting a partial-centering coefficient. It does not force effects orthogonal to predictors. R3 is eligible only after both R1 and R2 exhaust their authorized sampler attempts, and after numerical density, inverse, prior and likelihood equivalence validation passes.
