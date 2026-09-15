Explain metrics:
****************** Printing Vector Unit Statistics *******************
Vector Width:              4
Total Vector Instructions: 155
Vector Utilization:        86.0%
Utilized Vector Lanes:     533
Total Vector Lanes:        620
************************ Result Verification *************************
Passed!!!

- Quick example:
Iteration 1: [ *  *  *  * ] -> 4 lanes active
Iteration 2: [ *  *  _  * ] -> 3 lanes active (lane 2 is masked off)
Iteration 3: [ *  *  _  _ ] -> 2 lanes active (lanes 2 & 3 masked off)
...

- Vector Width: 
the number of parallel data elements (lanes) processed by a single SIMD vector intruction
hardware analogy - a 128-bit SIMD register operating on four 32-bit floats
simultaneously. Every vector instruction always processes a gang of 4 values at once

- Total Vector Instructions: 
the total count of SIMD instructions dispatched during execution

- Total Vector Lanes:
the total theoretical computation capacity of the vector execution units across the program

- Utilized Vector Lanes:
the actual number of lanes that did active, productive work (where the mask bit was 1 / true)

- Vector Utilization:
the hardware efficiency of your SIMD code
formula = Utilizied Vector Lanes / Total Vector Lanes

# What happens to the metrics when sweeping over the VECTOR_WIDTH?
VECTOR_WIDTH = 2 → 4 → 8 → 16
| Metric                    | As `VECTOR_WIDTH` increases                |
| ------------------------- | ------------------------------------------ |
| Total Vector Instructions | **decreases strongly**                     |
| Total Vector Lanes        | **increases somewhat**                     |
| Utilized Vector Lanes     | **roughly constant to slightly increases** |
| Vector Utilization %      | **decreases**                              |

- Total Vector Instructions:
decreases strongly because during each instruction, we can solve more problems, so iteratively, it decreases exponentially.
- Total Vector Lanes:
increases because each state terminates only when the largest exponent finishes, so it affects the total vector lanes even though the rest lanes in the vector had already finished a long time ago.
- Utilized Vector Lanes:
this is the tricky, intuitively it should remain constant because it only counts the active lanes within the vector - so the size of vector shouldn't affect the counting content within it. However, the logging doesn't "strictly" count the correct active lanes, e.g. cntbits() add all lanes into the log (more belove), so this metric tends to slightly increase.
- Vector Utilization:
decreases as Utilized Vector Lanes tends to remain constant (or slightly increase), while Total Vector Lanes increases.

. Before turning off the logging for _cs149_cntbits():
Vector Width:              4
Total Vector Instructions: 97075
Vector Utilization:        73.0%
Utilized Vector Lanes:     283585
Total Vector Lanes:        388300

Vector Width:              32
Total Vector Instructions: 14064
Vector Utilization:        66.5%
Utilized Vector Lanes:     299081
Total Vector Lanes:        450048

. After turning off the logging for _cs149_cntbits(): 
Vector Width:              4
Total Vector Instructions: 78432
Vector Utilization:        66.6%
Utilized Vector Lanes:     209013
Total Vector Lanes:        313728


Vector Width:              32
Total Vector Instructions: 11253
Vector Utilization:        58.1%
Utilized Vector Lanes:     209129
Total Vector Lanes:        360096

=> Utilized Vector Lanes change less (and with smaller values, ofc)




# CS149 Intrinsic Functions Syntax:

 _cs149_init_ones(<value>) creates a mask whose first <value> lanes are 1 and the remaining lanes are 0.
 _cs149_hadd_float() does "horizontal pairwise addition". In the fake library, it transforms:
  [a, b, c, d, e, f, g, h] --> [a+b, a+b, c+d, c+d, e+f, e+f, g+h, g+h]
  [1, 2, 3, 4, 5, 6, 7, 8] --> [3, 3, 7, 7, 11, 11, 15, 15]

 _cs149_interleave_float() does "vector interleaving". In the fake library, it transforms:
  [a, b, c, d, e, f, g, h] --> [a, e, b, f, c, g, d, h]
  [1, 2, 3, 4, 5, 6, 7, 8] --> [1, 5, 2, 6, 3, 7, 4, 8] or
  [3, 3, 7, 7, 11, 11, 15, 15] --> [3, 7, 11, 15, 3, 7, 11, 15] 

  (when repeat hadd and interleave, we'll have [36, 36, 36, 36, 36, 36, 36, 36])
