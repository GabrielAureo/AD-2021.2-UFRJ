import numpy as np
from scipy.stats import poisson
from numpy.linalg import matrix_power as mp
import math

def _rho(lamda, mu):
    return lamda/mu

def alpha(k, rho):
    return poisson.pmf(k, rho)

def beta_n(n, rho):
    if( n == 0 ):
        return 1
    def beta(k):
        return (((-1)**k)/math.factorial(k)) * ((n - k)**k) * (math.e**((n-k)*rho)) * (rho**k)    
    return sum([beta(_k) for _k in range(n + 1)])

def embedded_chain(N, lamda, mu):
    rho = _rho(lamda,mu)
    M = np.zeros(shape = (N,N))
    for i in range(N):
        lower = max(0,i - 1)
        for j in range(lower, N):
            M[i,j] = alpha(j - lower, rho)

    
    M[:, -1] = 1 - M.sum(axis = 1) + M[:, -1]
    return M

def mean_customers(N, lamda, mu):
    rho = _rho(lamda,mu)
    XN = N - (sum([beta_n(k, rho) for k in range(N-1 + 1)]) / (1 + (rho * beta_n(N-1, rho))) )
    return XN

def mean_wait(N, lamda, mu):
    rho = _rho(lamda,mu)
    T = 1/mu
    WN = (N - 1 - ((sum([beta_n(k, rho) for k in range(N - 1 + 1)] )  - N )/ (rho * beta_n(N - 1, rho)))) * T
    return WN
