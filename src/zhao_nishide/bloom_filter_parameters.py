"""Bloom filter parameters.

The parameters depend on the use case. Lower FP rates and longer keywords require more bits.
Suppose we have keywords w with length 15. Then, S_K(w) will contain 256 elements. We set the FP rate to 0.05.

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
             |-> m ~ 1600
p = 0.05    -/
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

m = 1600    -\
             |-> ceil(k) = 5
n = 256     -/
"""
BF_ARRAY_SIZE = 1600
BF_HASH_FUNCTIONS = 5
