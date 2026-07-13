"""Pure-python stats: Pearson r + two-tailed p, Spearman rho, OLS.

No numpy/scipy dependency by design, so this runs with a stock Python
install. The t-distribution CDF (for the Pearson p-value) is implemented
via the regularized incomplete beta function (Numerical Recipes betai/betacf).
"""
import math


def betacf(a, b, x, maxit=200, eps=3e-14, fpmin=1e-300):
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < fpmin: d = fpmin
    d = 1.0 / d
    h = d
    for m in range(1, maxit + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin: d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin: c = fpmin
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < fpmin: d = fpmin
        c = 1.0 + aa / c
        if abs(c) < fpmin: c = fpmin
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < eps:
            break
    return h


def betai(a, b, x):
    if x <= 0: return 0.0
    if x >= 1: return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * betacf(a, b, x) / a
    return 1.0 - bt * betacf(b, a, 1 - x) / b


def t_two_tailed_p(t, df):
    t = abs(t)
    return betai(df / 2.0, 0.5, df / (df + t * t))


def mean(v):
    return sum(v) / len(v)


def pearson(x, y):
    n = len(x)
    assert n == len(y) and n > 2
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return 0.0, 1.0
    r = max(-1.0, min(1.0, sxy / math.sqrt(sxx * syy)))
    df = n - 2
    if abs(r) >= 1.0:
        return r, 0.0
    t = r * math.sqrt(df / (1 - r * r))
    return r, t_two_tailed_p(t, df)


def rank(v):
    idx = sorted(range(len(v)), key=lambda i: v[i])
    ranks = [0.0] * len(v)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and v[idx[j + 1]] == v[idx[i]]:
            j += 1
        avg_rank = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[idx[k]] = avg_rank
        i = j + 1
    return ranks


def spearman(x, y):
    return pearson(rank(x), rank(y))


def ols(x, y):
    mx, my = mean(x), mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x)
    slope = sxy / sxx if sxx != 0 else 0.0
    return slope, my - slope * mx


def residuals_vs_time(y):
    t = list(range(len(y)))
    slope, intercept = ols(t, y)
    return [yi - (slope * ti + intercept) for ti, yi in zip(t, y)]


def diffs(v):
    return [v[i] - v[i - 1] for i in range(1, len(v))]
