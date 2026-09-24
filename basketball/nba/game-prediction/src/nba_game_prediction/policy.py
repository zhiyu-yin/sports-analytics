"""Stage 2 temporal access policy; no holdout override in this version."""
TRAIN=tuple(f'{y}-{str(y+1)[-2:]}' for y in range(2015,2023))
INTERNAL=TRAIN[3:]
VALIDATION='2023-24'
ALLOWED=TRAIN+(VALIDATION,)
def require_open(seasons):
    seasons=list(seasons)
    if not seasons or any(s not in ALLOWED for s in seasons):
        raise ValueError('Stage 2 season sealed, forbidden, missing or unsupported: '+str(seasons))
