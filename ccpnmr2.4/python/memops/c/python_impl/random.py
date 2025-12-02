"""
Pure Python implementation of random number generation.

This module implements the Linear Congruential Generator (LCG) algorithm
used in the original C code (random.c), providing compatibility with the
legacy CCPN random number generation.

The C implementation uses three LCGs combined with a shuffle buffer for
better randomness properties. This implementation maintains the same
algorithm and parameters for reproducibility.

Key algorithms:
1. Triple LCG: Three independent generators combined for better period
2. Shuffle buffer: 123-element array for improved randomness
3. Box-Muller transform: Converts uniform to normal distribution

Original C parameters:
- LCG1: M1=259200, A1=7141, C1=54773
- LCG2: M2=134456, A2=8121, C2=28411
- LCG3: M3=243000, A3=4561, C3=51349

Author: CCPN Team
License: LGPL
"""

import math


# LCG parameters from C code
RAN_ARRAY_SIZE = 123

M1 = 259200
A1 = 7141
C1 = 54773

M2 = 134456
A2 = 8121
C2 = 28411

M3 = 243000
A3 = 4561
C3 = 51349

R1 = 1.0 / M1
R2 = 1.0 / M2

TWOPI = 2.0 * math.pi


class RandomGenerator:
    """
    Linear Congruential Generator with shuffle buffer.
    
    This class maintains state for the random number generator,
    matching the behavior of the C implementation which uses
    static variables.
    
    The generator uses three LCGs:
    - LCG1 and LCG2: Combined to fill shuffle buffer
    - LCG3: Used to select from shuffle buffer
    
    This design improves randomness compared to a single LCG.
    """
    
    def __init__(self, seed=123456):
        """
        Initialize the random generator with a seed.
        
        Args:
            seed: Integer seed for reproducibility (default: 123456)
        """
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.ran_array = [0.0] * RAN_ARRAY_SIZE
        self.normal_next = 0.0
        self.normal_flag = True
        
        self.set_seed(seed)
    
    def set_seed(self, seed):
        """
        Set the seed for the random number generator.
        
        Initializes all three LCG states and fills the shuffle buffer.
        
        Args:
            seed: Unsigned integer seed
        """
        # Initialize LCG states
        self.x1 = (C1 + seed) % M1
        self.x1 = (A1 * self.x1 + C1) % M1
        self.x2 = self.x1 % M2
        self.x1 = (A1 * self.x1 + C1) % M1
        self.x3 = self.x1 % M3
        
        # Fill shuffle buffer
        for i in range(RAN_ARRAY_SIZE):
            self.x1 = (A1 * self.x1 + C1) % M1
            self.x2 = (A2 * self.x2 + C2) % M2
            self.ran_array[i] = (self.x1 + self.x2 * R2) * R1
        
        # Reset normal distribution state
        self.normal_flag = True
    
    def uniform01(self):
        """
        Generate uniform random number in [0, 1).
        
        Uses three LCGs with shuffle buffer:
        1. Advance all three generators
        2. Use x3 to select index in shuffle buffer
        3. Return selected value
        4. Replace selected value with new random number from x1, x2
        
        Returns:
            Float in range [0.0, 1.0)
        """
        # Advance all three LCGs
        self.x1 = (A1 * self.x1 + C1) % M1
        self.x2 = (A2 * self.x2 + C2) % M2
        self.x3 = (A3 * self.x3 + C3) % M3
        
        # Use x3 to select from shuffle buffer
        ind = (RAN_ARRAY_SIZE * self.x3) // M3
        r = self.ran_array[ind]
        
        # Refill buffer position with new random number
        self.ran_array[ind] = (self.x1 + self.x2 * R2) * R1
        
        return r
    
    def uniform(self, a, b):
        """
        Generate uniform random number in [a, b).
        
        Args:
            a: Lower bound (inclusive)
            b: Upper bound (exclusive)
            
        Returns:
            Float in range [a, b)
        """
        return a + (b - a) * self.uniform01()
    
    def normal01(self):
        """
        Generate normal random number with mean=0, std=1.
        
        Uses Box-Muller transform to convert two uniform random
        numbers into two independent normal random numbers.
        
        The transform generates pairs of values, so we cache one
        for the next call (using flag to track state).
        
        Box-Muller algorithm:
        1. Generate u1, u2 ~ Uniform(0,1)
        2. r = sqrt(-2 * ln(u1))
        3. theta = 2π * u2
        4. z1 = r * cos(theta), z2 = r * sin(theta)
        5. z1, z2 ~ Normal(0,1)
        
        Returns:
            Float from standard normal distribution N(0,1)
        """
        if self.normal_flag:
            self.normal_flag = False
            
            # Get u1, ensuring it's not zero (for log)
            x1 = self.uniform01()
            while x1 == 0:
                x1 = self.uniform01()
            
            # Get u2
            x2 = self.uniform01()
            
            # Box-Muller transform
            r = math.sqrt(-2.0 * math.log(x1))
            theta = TWOPI * x2
            
            y = r * math.cos(theta)
            self.normal_next = r * math.sin(theta)
            
            return y
        else:
            self.normal_flag = True
            return self.normal_next
    
    def normal(self, mean, std_dev):
        """
        Generate normal random number with specified mean and std dev.
        
        Args:
            mean: Mean of the distribution
            std_dev: Standard deviation of the distribution
            
        Returns:
            Float from normal distribution N(mean, std_dev²)
        """
        return mean + std_dev * self.normal01()


# Global generator instance (matches C static variables)
_global_generator = RandomGenerator()


# Module-level convenience functions (match C API)

def set_seed(seed):
    """
    Set seed for global random generator.
    
    Args:
        seed: Unsigned integer seed
    """
    _global_generator.set_seed(seed)


def uniform01():
    """
    Generate uniform random number in [0, 1).
    
    Returns:
        Float in range [0.0, 1.0)
    """
    return _global_generator.uniform01()


def uniform(a, b):
    """
    Generate uniform random number in [a, b).
    
    Args:
        a: Lower bound (inclusive)
        b: Upper bound (exclusive)
        
    Returns:
        Float in range [a, b)
    """
    return _global_generator.uniform(a, b)


def normal01():
    """
    Generate standard normal random number.
    
    Returns:
        Float from N(0,1)
    """
    return _global_generator.normal01()


def normal(mean, std_dev):
    """
    Generate normal random number.
    
    Args:
        mean: Mean of distribution
        std_dev: Standard deviation
        
    Returns:
        Float from N(mean, std_dev²)
    """
    return _global_generator.normal(mean, std_dev)


# Additional utility function for array generation
def uniform01_array(n):
    """
    Generate array of uniform random numbers.
    
    Args:
        n: Number of values to generate
        
    Returns:
        List of n uniform random values in [0, 1)
    """
    return [uniform01() for _ in range(n)]


def normal01_array(n):
    """
    Generate array of standard normal random numbers.
    
    Args:
        n: Number of values to generate
        
    Returns:
        List of n standard normal random values
    """
    return [normal01() for _ in range(n)]
