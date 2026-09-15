import subprocess
import re
import os
import shutil
import matplotlib.pyplot as plt

def run_benchmark_turbo():
    thread_counts = list(range(2, 17))  # 2 to 16 as requested
    all_threads = [1] + thread_counts
    
    results = []
    serial_times = []

    print("=" * 60)
    print(" Running Benchmark for Mandelbrot Turbo (Interleaved Rows)")
    print("=" * 60)
    print(f"{'Threads':<10} | {'Serial (ms)':<14} | {'Turbo (ms)':<14} | {'Speedup':<10}")
    print("-" * 60)

    for t in all_threads:
        cmd = ["wsl", "./mandelbrot_turbo", "--threads", str(t)]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        out = proc.stdout

        serial_match = re.search(r'\[mandelbrot serial\]:\s*\[([\d\.]+)\]\s*ms', out)
        thread_match = re.search(r'\[mandelbrot thread\]:\s*\[([\d\.]+)\]\s*ms', out)
        speedup_match = re.search(r'\(([\d\.]+)x speedup from', out)

        if not (serial_match and thread_match and speedup_match):
            print(f"Error parsing output for {t} threads:\n{out}")
            continue

        s_time = float(serial_match.group(1))
        t_time = float(thread_match.group(1))
        speedup = float(speedup_match.group(1))

        serial_times.append(s_time)
        results.append({
            'threads': t,
            'serial_ms': s_time,
            'thread_ms': t_time,
            'speedup': speedup
        })

        print(f"{t:<10} | {s_time:<14.3f} | {t_time:<14.3f} | {speedup:<10.2f}x")

    avg_serial = sum(r['serial_ms'] for r in results) / len(results)

    # Save to CSV
    csv_path = "benchmark_turbo_results.csv"
    with open(csv_path, "w") as f:
        f.write("threads,serial_ms,turbo_ms,speedup\n")
        for r in results:
            f.write(f"{r['threads']},{r['serial_ms']:.3f},{r['thread_ms']:.3f},{r['speedup']:.2f}\n")
    print(f"\nResults saved to {csv_path}")

    # Plotting
    threads = [r['threads'] for r in results]
    times = [r['thread_ms'] for r in results]
    speedups = [r['speedup'] for r in results]

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#ffffff')

    # Subplot 1: Execution Time
    ax1.plot(threads, times, marker='o', color='#8b5cf6', linewidth=2.5, markersize=7, label='Turbo Time (Interleaved)', zorder=4)
    ax1.axhline(avg_serial, color='#dc2626', linestyle='--', linewidth=1.8, label=f'Serial Baseline ({avg_serial:.1f} ms)', zorder=3)
    ax1.set_title('Execution Time vs. Thread Count', fontsize=14, fontweight='bold', pad=12)
    ax1.set_xlabel('Number of Threads', fontsize=12, labelpad=8)
    ax1.set_ylabel('Execution Time (ms)', fontsize=12, labelpad=8)
    ax1.set_xticks(threads)
    ax1.grid(True, linestyle='--', alpha=0.6)
    ax1.legend(fontsize=11, frameon=True, facecolor='white', framealpha=0.9)

    # Annotate points on time plot
    for t, tm in zip(threads, times):
        if t in [1, 2, 3, 4, 8, 12, 16]:
            ax1.annotate(f"{tm:.1f}ms", (t, tm), textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=9, fontweight='semibold', color='#5b21b6')

    # Subplot 2: Speedup Ratio
    ax2.plot(threads, speedups, marker='s', color='#059669', linewidth=2.5, markersize=7, label='Turbo Speedup', zorder=4)
    ax2.plot(threads, threads, color='#9ca3af', linestyle=':', linewidth=1.8, label='Ideal Linear Speedup (T)', zorder=3)
    ax2.set_title('Speedup Ratio vs. Thread Count', fontsize=14, fontweight='bold', pad=12)
    ax2.set_xlabel('Number of Threads', fontsize=12, labelpad=8)
    ax2.set_ylabel('Speedup Factor', fontsize=12, labelpad=8)
    ax2.set_xticks(threads)
    ax2.grid(True, linestyle='--', alpha=0.6)
    ax2.legend(fontsize=11, frameon=True, facecolor='white', framealpha=0.9)

    # Annotate points on speedup plot
    for t, sp in zip(threads, speedups):
        if t in [1, 2, 3, 4, 8, 12, 16]:
            ax2.annotate(f"{sp:.2f}x", (t, sp), textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=9, fontweight='semibold', color='#065f46')

    plt.suptitle('CS149 Mandelbrot Turbo Thread Scaling (Interleaved Rows - View 1)', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()

    out_plot = "mandelbrot_turbo_scaling.png"
    plt.savefig(out_plot, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {out_plot}")

    # Copy to artifact directory if available
    artifact_dir = r"C:\Users\voqua\.gemini\antigravity-ide\brain\26747796-ec0d-4afa-b9ea-a7bd5084c49b"
    if os.path.exists(artifact_dir):
        artifact_plot = os.path.join(artifact_dir, "mandelbrot_turbo_scaling.png")
        shutil.copyfile(out_plot, artifact_plot)
        print(f"Plot copied to artifact dir: {artifact_plot}")

if __name__ == "__main__":
    run_benchmark_turbo()
