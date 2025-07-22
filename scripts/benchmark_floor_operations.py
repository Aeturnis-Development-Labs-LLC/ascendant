"""Benchmark script for floor operations."""

import time
import statistics
from typing import List, Tuple

from src.models.floor import Floor


def benchmark_operation(operation_name: str, operation, iterations: int = 100) -> Tuple[float, float, float]:
    """Benchmark an operation and return min, avg, max times in milliseconds."""
    times = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        operation()
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    return min(times), statistics.mean(times), max(times)


def benchmark_floor_generation(seed: int = 12345) -> Tuple[float, float, float]:
    """Benchmark floor generation."""
    def operation():
        floor = Floor(seed)
        floor.generate()
    
    return benchmark_operation("Floor Generation", operation)


def benchmark_room_connection(seed: int = 12345) -> Tuple[float, float, float]:
    """Benchmark room connection (excluding floor generation)."""
    # Pre-generate floor
    floor = Floor(seed)
    floor.generate()
    
    def operation():
        # Reset tiles to walls for rooms
        for room in floor.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    floor.tiles[(x, y)].tile_type = floor.tiles[(x, y)].tile_type
        floor.connect_rooms()
    
    return benchmark_operation("Room Connection", operation)


def benchmark_pathfinding_check(seed: int = 12345) -> Tuple[float, float, float]:
    """Benchmark pathfinding connectivity check."""
    # Pre-generate and connect floor
    floor = Floor(seed)
    floor.generate()
    floor.connect_rooms()
    
    def operation():
        floor.is_fully_connected()
    
    return benchmark_operation("Pathfinding Check", operation)


def benchmark_full_floor_creation(seed: int = 12345) -> Tuple[float, float, float]:
    """Benchmark complete floor creation including all steps."""
    def operation():
        floor = Floor(seed)
        floor.generate()
        floor.connect_rooms()
        floor.place_stairs()
        floor.is_fully_connected()
    
    return benchmark_operation("Full Floor Creation", operation, iterations=50)


def main():
    """Run all benchmarks and display results."""
    print("=== ASCENT Floor Operations Benchmark ===")
    print(f"Running {100} iterations for each operation...")
    print()
    
    # Test with different seeds to ensure consistency
    seeds = [12345, 54321, 99999, 11111, 77777]
    
    # Aggregate results
    gen_times = []
    conn_times = []
    path_times = []
    full_times = []
    
    for seed in seeds:
        gen_min, gen_avg, gen_max = benchmark_floor_generation(seed)
        conn_min, conn_avg, conn_max = benchmark_room_connection(seed)
        path_min, path_avg, path_max = benchmark_pathfinding_check(seed)
        full_min, full_avg, full_max = benchmark_full_floor_creation(seed)
        
        gen_times.append(gen_avg)
        conn_times.append(conn_avg)
        path_times.append(path_avg)
        full_times.append(full_avg)
    
    # Display results
    print("### Individual Operation Benchmarks (milliseconds)")
    print("| Operation | Min | Avg | Max | Target | Status |")
    print("|-----------|-----|-----|-----|--------|--------|")
    
    # Floor Generation
    gen_overall_avg = statistics.mean(gen_times)
    gen_status = "PASS" if gen_overall_avg < 100 else "FAIL"
    print(f"| Floor Generation | {min(gen_times):.2f} | {gen_overall_avg:.2f} | {max(gen_times):.2f} | <100ms | {gen_status} |")
    
    # Room Connection
    conn_overall_avg = statistics.mean(conn_times)
    conn_status = "PASS" if conn_overall_avg < 50 else "FAIL"
    print(f"| Room Connection | {min(conn_times):.2f} | {conn_overall_avg:.2f} | {max(conn_times):.2f} | <50ms | {conn_status} |")
    
    # Pathfinding Check
    path_overall_avg = statistics.mean(path_times)
    path_status = "PASS" if path_overall_avg < 50 else "FAIL"
    print(f"| Pathfinding Check | {min(path_times):.2f} | {path_overall_avg:.2f} | {max(path_times):.2f} | <50ms | {path_status} |")
    
    print()
    print("### Combined Operations")
    print("| Operation | Min | Avg | Max | Target | Status |")
    print("|-----------|-----|-----|-----|--------|--------|")
    
    # Full Floor Creation
    full_overall_avg = statistics.mean(full_times)
    full_status = "PASS" if full_overall_avg < 500 else "FAIL"
    print(f"| Full Floor Creation | {min(full_times):.2f} | {full_overall_avg:.2f} | {max(full_times):.2f} | <500ms | {full_status} |")
    
    print()
    print("### Performance by Seed")
    print("| Seed | Floor Gen | Room Conn | Path Check | Full Create |")
    print("|------|-----------|-----------|------------|-------------|")
    for i, seed in enumerate(seeds):
        print(f"| {seed} | {gen_times[i]:.2f}ms | {conn_times[i]:.2f}ms | {path_times[i]:.2f}ms | {full_times[i]:.2f}ms |")
    
    print()
    print("### Summary")
    all_pass = all([gen_overall_avg < 100, conn_overall_avg < 50, path_overall_avg < 50, full_overall_avg < 500])
    if all_pass:
        print("All performance benchmarks PASSED!")
    else:
        print("Some performance benchmarks failed.")
    
    print()
    print(f"Note: Benchmarks run on current hardware and may vary.")
    print(f"Target times are based on CAFE methodology requirements.")


if __name__ == "__main__":
    main()