import time
import tracemalloc

class BenchmarkRunner:
    @staticmethod
    def measure_execution(func, *args, **kwargs) -> dict:
        """
        Ejecuta una función algorítmica y retorna:
        - Resultado
        - Tiempo de ejecución en milisegundos
        - Consumo de memoria en KB
        """
        tracemalloc.start()
        start_time = time.perf_counter()

        # Ejecución del algoritmo
        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        current_mem, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        execution_time_ms = (end_time - start_time) * 1000
        peak_memory_kb = peak_mem / 1024

        return {
            "result": result,
            "metrics": {
                "execution_time_ms": round(execution_time_ms, 4),
                "peak_memory_kb": round(peak_memory_kb, 2)
            }
        }