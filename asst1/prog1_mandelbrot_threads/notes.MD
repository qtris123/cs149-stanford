Note: the CPU used to run these programs is AMD Ryzen 9 7940HS 16-Core Processor, each core has 2 SMT threads.

# 1, 2, 3:
Look at the mandelbrot_scaling.png figure to see how performance looks like as we increase the number of Threads

# 4:
We change the rows-to-thread assigment policy in mandelbrot_turbo. The mandelbrot computation has a terrible workload distribution. Firstly, the closer to the center of the image, the calculation there gets more time consuming. Secondly, and the reason of this loadbalancing policy, rows of the same workload intensity usually clusters together - for example, L L L M M M H H L L L M M...
In the first version, we assigned rows contiguously, increasing the chance of the same thread tacking the same intense rows and vice versa.
Solution:  cyclic assigment
- Thread 0: row 0, T, 2T, 3T ...
- Thread 1: row 1, 1+T, 1+2T, 1+3T ...

Since each thread handles 1 specific row, no need for synchronization. Refernence the mandelbrot_turbo_scaling.png to see the performance

# 5:

SMT = Simultaneous Multithreading. AMD's CPUs use SMT; Intel's closely related branding is Hyper-Threading

Our CPU, Ryzen 9 5900HS, looks conceptually like this:

8 physical cores
│
├── Core 0 ── hardware thread A
│          └─ hardware thread B
│
├── Core 1 ── hardware thread A
│          └─ hardware thread B
│
...
└── Core 7 ── hardware thread A
           └─ hardware thread B

= 16 logical CPUs

However, 16 logical CPUs != 16 physical cores, due to two SMT threads on the same physical core share much of that core's hardware.
                Physical Core
              ┌─────────────────┐
Thread A ─────►│                 │
               │ execution units│
               │ caches         │
               │ pipelines      │
Thread B ─────►│                 │
              └─────────────────┘

So SMT is useful when one thread cannot fully utilize a core, then the CPU will start another thread while, e.g., waiting for the previous thread to finish. If both threads are active, they will compete for core resources like execution units, caches, and pipelines, which can limit overall performance.

## The difference between our AMD and Stanford's Intel Myth
We have 16 cores, while their Myth has 8 cores only. So there are enough physical cores to give each worker.
=> Multicore Parallelism

We only exploit SMT when we use more than 16 threads.

And Oversubscription starts when you have more runnable software threads than hardware contexts (physical cores × SMT threads)
For example, if you run four software threads on that physical core's two SMT contexts:

software A ─┐
software B ─┼──> only 2 hardware contexts
software C ─┤
software D ─┘

The OS must time-share them:

time ──────────────────────────>

SMT context 0:
A A A | C C C | A A A | C C C

SMT context 1:
B B B | D D D | B B B | D D D

Difference:
SMT = hardware sharing within a physical core.
Oversubscription = software scheduling more runnable threads than the hardware has execution contexts for.

