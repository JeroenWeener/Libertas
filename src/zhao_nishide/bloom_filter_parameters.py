"""Bloom filter parameters.

Suppose we have keywords w with length 15. Then, S_K(w) will contain 256 elements. We set the FP rate to 0.01.

Bloom filter size
-----------------
m = -(n * log(p)) / (log(2)^2)
m : int
    number of bits in the Bloom filter
n : int
    number of items expected to be stored in the Bloom filter
p : float
    FP rate (0-1)

n = 256     -\
             |-> m = 2454 ~ 2500
p = 0.01    -/
-----------------

Number of hash functions
-----------------
k = (m/n) * log(2)
k : int
    number of hash functions
m : int
    size of bits in the Bloom filter
n : int
    number of items expected to be stored in the Bloom filter

m = 2500    -\
             |-> k ~ 7
n = 256     -/
"""
BF_ARRAY_SIZE = 2500
BF_HASH_FUNCTIONS = 7
