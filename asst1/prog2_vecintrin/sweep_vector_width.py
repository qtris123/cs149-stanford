import subprocess
import re
import os
import shutil
import matplotlib.pyplot as plt

HEADER_FILE = "CS149intrin.h"
CSV_FILE = "vector_width_results.csv"
PLOT_FILE = "vector_width_scaling.png"
ARTIFACT_DIR = r"C:\Users\voqua\.gemini\antigravity-ide\brain\26747796-ec0d-4afa-b9ea-a7bd5084c49b"

def set_vector_width(width):
    with open(HEADER_FILE, "r") as f:
        content = f.read()
    new_content = re.sub(r'#define\s+VECTOR_WIDTH\s+\d+', f'#define VECTOR_WIDTH {width}', content)
    with open(HEADER_FILE, "w") as f:
        f.write(new_content)

def run_experiment(widths=[2, 4, 8, 16], size=10000):
    # Backup original header content
    with open(HEADER_FILE, "r") as f:
        original_header = f.read()

    results = []
    print("=" * 75)
    print(f" Sweeping VECTOR_WIDTH in {widths} with size N={size}")
    print("=" * 75)
    print(f"{'Width':<8} | {'Instructions':<14} | {'Utilization':<14} | {'Utilized Lanes':<16} | {'Total Lanes':<12}")
    print("-" * 75)

    try:
        for w in widths:
            set_vector_width(w)
            
            # Recompile
            build_cmd = ["wsl", "make", "clean"]
            subprocess.run(build_cmd, capture_output=True, text=True, check=True)
            build_cmd = ["wsl", "make"]
            subprocess.run(build_cmd, capture_output=True, text=True, check=True)

            # Run benchmark
            run_cmd = ["wsl", "./myexp", "-s", str(size)]
            proc = subprocess.run(run_cmd, capture_output=True, text=True)
            out = proc.stdout

            # Parse stats
            w_match = re.search(r'Vector Width:\s*(\d+)', out)
            inst_match = re.search(r'Total Vector Instructions:\s*(\d+)', out)
            util_match = re.search(r'Vector Utilization:\s*([\d\.]+)%', out)
            util_lanes_match = re.search(r'Utilized Vector Lanes:\s*(\d+)', out)
            total_lanes_match = re.search(r'Total Vector Lanes:\s*(\d+)', out)

            if not (inst_match and util_match and util_lanes_match and total_lanes_match):
                print(f"Failed to parse output for width {w}:\n{out}")
                continue

            inst = int(inst_match.group(1))
            util = float(util_match.group(1))
            util_lanes = int(util_lanes_match.group(1))
            total_lanes = int(total_lanes_match.group(1))

            results.append({
                'width': w,
                'instructions': inst,
                'utilization': util,
                'utilized_lanes': util_lanes,
                'total_lanes': total_lanes
            })

            print(f"{w:<8} | {inst:<14} | {util:<13.1f}% | {util_lanes:<16} | {total_lanes:<12}")

    finally:
        # Restore original header file
        with open(HEADER_FILE, "w") as f:
            f.write(original_header)
        # Rebuild with restored header
        subprocess.run(["wsl", "make"], capture_output=True, text=True)

    # Save to CSV
    with open(CSV_FILE, "w") as f:
        f.write("width,instructions,utilization_pct,utilized_lanes,total_lanes\n")
        for r in results:
            f.write(f"{r['width']},{r['instructions']},{r['utilization']:.1f},{r['utilized_lanes']},{r['total_lanes']}\n")
    print(f"\nResults saved to {CSV_FILE}")

    # Plotting 2x2 grid
    plot_results(results, size)

def plot_results(results, size):
    widths = [r['width'] for r in results]
    x_pos = range(len(widths))
    x_labels = [str(w) for w in widths]

    instructions = [r['instructions'] for r in results]
    utilizations = [r['utilization'] for r in results]
    utilized_lanes = [r['utilized_lanes'] for r in results]
    total_lanes = [r['total_lanes'] for r in results]

    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#ffffff')

    # 1. Total Vector Instructions
    ax1 = axes[0, 0]
    ax1.plot(x_pos, instructions, marker='o', color='#2563eb', linewidth=2.5, markersize=8)
    ax1.set_title('Total Vector Instructions', fontsize=13, fontweight='bold', pad=10)
    ax1.set_xlabel('Vector Width', fontsize=11)
    ax1.set_ylabel('Instruction Count', fontsize=11)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(x_labels)
    ax1.grid(True, linestyle='--', alpha=0.6)
    for i, val in enumerate(instructions):
        ax1.annotate(f"{val:,}", (i, val), textcoords="offset points", xytext=(0, 10),
                     ha='center', fontsize=9, fontweight='semibold', color='#1e3a8a')

    # 2. Vector Utilization (%)
    ax2 = axes[0, 1]
    ax2.plot(x_pos, utilizations, marker='s', color='#059669', linewidth=2.5, markersize=8)
    ax2.set_title('Vector Utilization (%)', fontsize=13, fontweight='bold', pad=10)
    ax2.set_xlabel('Vector Width', fontsize=11)
    ax2.set_ylabel('Utilization (%)', fontsize=11)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(x_labels)
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle='--', alpha=0.6)
    for i, val in enumerate(utilizations):
        ax2.annotate(f"{val:.1f}%", (i, val), textcoords="offset points", xytext=(0, 10),
                     ha='center', fontsize=9, fontweight='semibold', color='#065f46')

    # 3. Utilized Vector Lanes
    ax3 = axes[1, 0]
    ax3.plot(x_pos, utilized_lanes, marker='^', color='#7c3aed', linewidth=2.5, markersize=8)
    ax3.set_title('Utilized Vector Lanes', fontsize=13, fontweight='bold', pad=10)
    ax3.set_xlabel('Vector Width', fontsize=11)
    ax3.set_ylabel('Utilized Lanes', fontsize=11)
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(x_labels)
    ax3.grid(True, linestyle='--', alpha=0.6)
    for i, val in enumerate(utilized_lanes):
        ax3.annotate(f"{val:,}", (i, val), textcoords="offset points", xytext=(0, 10),
                     ha='center', fontsize=9, fontweight='semibold', color='#4c1d95')

    # 4. Total Vector Lanes
    ax4 = axes[1, 1]
    ax4.plot(x_pos, total_lanes, marker='D', color='#d97706', linewidth=2.5, markersize=8)
    ax4.set_title('Total Vector Lanes', fontsize=13, fontweight='bold', pad=10)
    ax4.set_xlabel('Vector Width', fontsize=11)
    ax4.set_ylabel('Total Lanes', fontsize=11)
    ax4.set_xticks(x_pos)
    ax4.set_xticklabels(x_labels)
    ax4.grid(True, linestyle='--', alpha=0.6)
    for i, val in enumerate(total_lanes):
        ax4.annotate(f"{val:,}", (i, val), textcoords="offset points", xytext=(0, 10),
                     ha='center', fontsize=9, fontweight='semibold', color='#78350f')

    plt.suptitle(f'CS149 Vector Unit Metrics vs. VECTOR_WIDTH (N = {size:,})', fontsize=16, fontweight='bold', y=0.99)
    plt.tight_layout()

    plt.savefig(PLOT_FILE, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {PLOT_FILE}")

    if os.path.exists(ARTIFACT_DIR):
        artifact_plot = os.path.join(ARTIFACT_DIR, PLOT_FILE)
        shutil.copyfile(PLOT_FILE, artifact_plot)
        print(f"Plot copied to artifact dir: {artifact_plot}")

if __name__ == "__main__":
    run_experiment([2, 4, 8, 16], size=10000)
