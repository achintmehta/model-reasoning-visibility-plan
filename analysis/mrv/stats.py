"""Stratified permutation tests, Holm's correction, the stratified bootstrap and the
equivalence verdict (protocol sections 8.1 and 8.2). Numpy only.

Every function takes one unit per element: `values` (float), `is_b` (True for the treatment
arm b, False for the reference arm a) and `strata` (any hashable label per unit). Units whose
value is NaN are dropped before anything is computed.
"""
import numpy as np


def _clean(values, is_b, strata):
    values = np.asarray(values, dtype=float)
    is_b = np.asarray(is_b, dtype=bool)
    strata = np.asarray(strata, dtype=object)
    keep = ~np.isnan(values)
    return values[keep], is_b[keep], strata[keep]


def _groups(strata):
    out = {}
    for i, s in enumerate(strata):
        out.setdefault(s, []).append(i)
    return [np.array(v, dtype=int) for _, v in sorted(out.items(), key=lambda kv: str(kv[0]))]


def mean_diff(values, is_b):
    """The statistic of every test: mean of arm b minus mean of arm a."""
    if is_b.sum() == 0 or (~is_b).sum() == 0:
        return float("nan")
    return float(values[is_b].mean() - values[~is_b].mean())


def perm_test(values, is_b, strata, n_perm, rng, alternative="two-sided", detail=None):
    """Stratified permutation test of the difference in means (b minus a).

    The arm labels are permuted within each stratum, keeping each stratum's count of b units.
    Returns (observed difference, p value, n_a, n_b). alternative is "two-sided", "greater"
    (b above a) or "less" (b below a). p = (1 + number of permuted values at least as extreme)
    / (n_perm + 1).
    If `detail` is a dict, it receives the observed statistic, every permuted statistic, the
    number at least as extreme, and the tolerance used to compare them.
    """
    v, b, s = _clean(values, is_b, strata)
    n_a, n_b = int((~b).sum()), int(b.sum())
    if n_a == 0 or n_b == 0:
        return float("nan"), float("nan"), n_a, n_b
    t_obs = mean_diff(v, b)
    labels = np.zeros((n_perm, v.size), dtype=bool)
    for idx in _groups(s):
        k, m = idx.size, int(b[idx].sum())
        if m == 0:
            continue
        if m == k:
            labels[:, idx] = True
            continue
        keys = rng.random((n_perm, k))
        ranks = np.argsort(np.argsort(keys, axis=1), axis=1)
        labels[:, idx] = ranks < m
    sum_b = labels.astype(float) @ v
    t = sum_b / n_b - (v.sum() - sum_b) / n_a
    eps = 1e-12 * max(1.0, abs(t_obs))
    if alternative == "two-sided":
        extreme = np.abs(t) >= abs(t_obs) - eps
    elif alternative == "greater":
        extreme = t >= t_obs - eps
    elif alternative == "less":
        extreme = t <= t_obs + eps
    else:
        raise ValueError(alternative)
    p = (1.0 + float(extreme.sum())) / (n_perm + 1.0)
    if detail is not None:
        detail.update({"t_obs": t_obs, "t_star": t, "extreme": int(extreme.sum()), "eps": eps})
    return t_obs, p, n_a, n_b


def _boot_means(values, strata, n_boot, rng, transform=None):
    """Bootstrap means of one arm: units resampled with replacement inside each stratum.

    Each stratum's resampled mean is rescaled about the stratum's own mean by sqrt(k / (k - 1)),
    k the stratum's size, so that its bootstrap variance equals the usual unbiased one. Without
    it the plain bootstrap understates the variance by (k - 1) / k, which at 10 sampled apps a
    stratum makes the 95% quality interval cover about 93% (DESIGN.md section 10 item 3).
    The arm's mean is the strata's means weighted by their sizes.
    """
    x = values if transform is None else transform(values)
    total = np.zeros(n_boot)
    for idx in _groups(strata):
        k = idx.size
        xs = x[idx]
        m = xs[rng.integers(0, k, size=(n_boot, k))].mean(axis=1)
        if k > 1:
            m = xs.mean() + np.sqrt(k / (k - 1.0)) * (m - xs.mean())
        total += m * k
    return total / x.size


def bootstrap(values, is_b, strata, n_boot, rng, kind="diff"):
    """Stratified bootstrap of a contrast between arm b and arm a.

    kind "diff": mean(b) - mean(a). kind "ratio_of_means": mean(b) / mean(a).
    kind "ratio_geo": exp(mean log b - mean log a), for values already on the log scale.
    Returns (estimate, array of bootstrap replicates).
    """
    v, b, s = _clean(values, is_b, strata)
    if b.sum() == 0 or (~b).sum() == 0:
        return float("nan"), np.array([])
    mb = _boot_means(v[b], s[b], n_boot, rng)
    ma = _boot_means(v[~b], s[~b], n_boot, rng)
    if kind == "diff":
        return float(v[b].mean() - v[~b].mean()), mb - ma
    if kind == "ratio_of_means":
        with np.errstate(divide="ignore", invalid="ignore"):
            return float(v[b].mean() / v[~b].mean()), mb / ma
    if kind == "ratio_geo":
        return float(np.exp(v[b].mean() - v[~b].mean())), np.exp(mb - ma)
    raise ValueError(kind)


def percentile_ci(replicates, level):
    """The percentile interval of bootstrap replicates at the given level (0.95 or 0.90)."""
    r = np.asarray(replicates, dtype=float)
    r = r[np.isfinite(r)]
    if r.size == 0:
        return float("nan"), float("nan")
    lo = (1.0 - level) / 2.0
    q = np.quantile(r, [lo, 1.0 - lo])
    return float(q[0]), float(q[1])


def holm(pvalues):
    """Holm's step-down adjusted p values, in the input order. NaN stays NaN."""
    p = np.asarray(pvalues, dtype=float)
    out = np.full(p.shape, np.nan)
    ok = np.where(~np.isnan(p))[0]
    order = ok[np.argsort(p[ok], kind="stable")]
    m = order.size
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, min(1.0, (m - rank) * p[i]))
        out[i] = running
    return out


def holm_steps(pvalues):
    """Holm's procedure step by step, in the input order: each p's rank in the sorted order,
    its multiplier (m - rank + 1), the product capped at 1, and the running maximum, which is
    the adjusted p. NaN p values take no part."""
    p = np.asarray(pvalues, dtype=float)
    ok = np.where(~np.isnan(p))[0]
    order = ok[np.argsort(p[ok], kind="stable")]
    m = order.size
    out = [{"rank": None, "multiplier": None, "product": float("nan"), "adjusted": float("nan")} for _ in p]
    running = 0.0
    for rank, i in enumerate(order):
        prod = min(1.0, (m - rank) * p[i])
        running = max(running, prod)
        out[i] = {"rank": rank + 1, "multiplier": m - rank, "product": prod, "adjusted": running}
    return out


def verdict(p_adjusted, ci90, bounds, alpha=0.05):
    """The three-way verdict of protocol section 8.2.

    "different" if the Holm-adjusted p is below alpha. Otherwise "equivalent" if bounds are given
    and the 90% interval lies wholly inside them. Otherwise "undetermined".
    """
    if p_adjusted == p_adjusted and p_adjusted < alpha:
        return "different"
    if bounds is not None and ci90[0] == ci90[0]:
        lo, hi = bounds
        if lo < ci90[0] and ci90[1] < hi:
            return "equivalent"
    return "undetermined"


def largest_excluded(ci90):
    """X of "changes nothing by more than X": the largest absolute end of the 90% interval."""
    return max(abs(ci90[0]), abs(ci90[1]))


def boot_mean(values, strata, n_boot, rng):
    """One arm's mean and its stratified bootstrap replicates (for the descriptives)."""
    v = np.asarray(values, dtype=float)
    s = np.asarray(strata, dtype=object)
    keep = ~np.isnan(v)
    v, s = v[keep], s[keep]
    if v.size == 0:
        return float("nan"), np.array([])
    return float(v.mean()), _boot_means(v, s, n_boot, rng)


# ---------------------------------------------------------------- shares: Wilson and Newcombe

def _z(level):
    from statistics import NormalDist
    return NormalDist().inv_cdf(0.5 + level / 2.0)


def wilson(x, n, level=0.95):
    """Wilson score interval of a share of x in n."""
    if n == 0:
        return float("nan"), float("nan")
    z = _z(level)
    p = x / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2.0 * n)) / d
    h = z * np.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n)) / d
    return float(max(0.0, c - h)), float(min(1.0, c + h))


def newcombe_parts(xa, na, xb, nb, level=0.95):
    """Every piece of Newcombe's interval: the two shares, their Wilson intervals, z, and the
    interval itself (b minus a)."""
    lo, hi = newcombe(xa, na, xb, nb, level)
    la, ua = wilson(xa, na, level)
    lb, ub = wilson(xb, nb, level)
    return {"z": _z(level), "p_a": xa / na if na else float("nan"), "p_b": xb / nb if nb else float("nan"),
            "wilson_a_lo": la, "wilson_a_hi": ua, "wilson_b_lo": lb, "wilson_b_hi": ub, "lo": lo, "hi": hi}


def newcombe(xa, na, xb, nb, level=0.95):
    """Newcombe's hybrid score interval of the difference of two shares, b minus a (his
    method 10). Used for every difference between two shares of runs (DESIGN.md section 10)."""
    if na == 0 or nb == 0:
        return float("nan"), float("nan")
    pa, pb = xa / na, xb / nb
    la, ua = wilson(xa, na, level)
    lb, ub = wilson(xb, nb, level)
    d = pb - pa
    return (float(d - np.sqrt((pb - lb) ** 2 + (ua - pa) ** 2)),
            float(d + np.sqrt((ub - pb) ** 2 + (pa - la) ** 2)))


def mover_diff(d1, ci1, d2, ci2):
    """The interval of d1 minus d2 from the intervals of d1 and of d2, by the method of variance
    estimates recovery (Zou and Donner), the construction Newcombe's interval is itself made by.
    Used for the within-lab pairs' difference of two failure differences."""
    (l1, u1), (l2, u2) = ci1, ci2
    d = d1 - d2
    return (float(d - np.sqrt((d1 - l1) ** 2 + (u2 - d2) ** 2)),
            float(d + np.sqrt((u1 - d1) ** 2 + (d2 - l2) ** 2)))
