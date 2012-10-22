# Calculate (28433 * 2^7830457+1) mod 10^10
base = 10000000000

def power_mod(n, exponent, base):
    if exponent == 0:
        return 1
    tmp = power_mod(n * n % base, exponent / 2, base)
    if (exponent % 2 != 0):
        tmp = tmp * n % base
    return tmp

print power_mod(2, 7830457, 100) * 28433 % base + 1