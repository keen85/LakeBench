from typing import Optional
from ..base import BaseBenchmark
from ...utils.timer import timer
from .engines.spark import SparkAtomicELT
from .engines.duckdb import DuckDBAtomicELT
from .engines.daft import DaftAtomicELT
from .engines.polars import PolarsAtomicELT

from ...engines.base import BaseEngine
from ...engines.spark import Spark
from ...engines.duckdb import DuckDB
from ...engines.daft import Daft
from ...engines.polars import Polars

import importlib.resources

class TPCDS(BaseBenchmark):
    """
    LightMode: minimal benchmark for quick comparisons.
    Includes basic ELT actions: load data, simple transforms, incremental processing, maintenance jobs, small query.
    """

    BENCHMARK_IMPL_REGISTRY = {
        Spark: SparkAtomicELT,
        DuckDB: DuckDBAtomicELT,
        Daft: DaftAtomicELT,
        Polars: PolarsAtomicELT
    }

    def __init__(
            self, 
            engine: BaseEngine, 
            scenario_name: str,
            mode: str,
            query_list: Optional[list],
            tpcds_parquet_mount_path: Optional[str],
            tpcds_parquet_abfss_path: Optional[str],
            result_abfss_path: Optional[str],
            save_results: bool = False
            ):
        super().__init__(engine, scenario_name, result_abfss_path, save_results)
        self.MODE_REGISTRY = ['load', 'query', 'power_test']
        if mode not in self.MODE_REGISTRY:
            raise ValueError(f"Mode '{mode}' is not supported. Supported modes: {self.MODE_REGISTRY}.")
        else:
            self.mode = mode 
        self.TABLE_REGISTRY = [
            'call_center', 'catalog_page', 'catalog_returns', 'catalog_sales',
            'customer', 'customer_address', 'customer_demographics', 'date_dim',
            'household_demographics', 'income_band', 'inventory', 'item',
            'promotion', 'reason', 'ship_mode', 'store', 'store_returns',
            'store_sales', 'time_dim', 'warehouse', 'web_page', 'web_returns',
            'web_sales', 'web_site'
        ]
        self.QUERY_REGISTRY = [
            'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10',
            'q11', 'q12', 'q13', 'q14a', 'q14b', 'q15', 'q16', 'q17', 'q18', 'q19', 'q20',
            'q21', 'q22', 'q23a', 'q23b', 'q24a', 'q24b', 'q25', 'q26', 'q27', 'q28', 'q29', 'q30',
            'q31', 'q32', 'q33', 'q34', 'q35', 'q36', 'q37', 'q38', 'q39a', 'q39b', 'q40',
            'q41', 'q42', 'q43', 'q44', 'q45', 'q46', 'q47', 'q48', 'q49', 'q50',
            'q51', 'q52', 'q53', 'q54', 'q55', 'q56', 'q57', 'q58', 'q59', 'q60',
            'q61', 'q62', 'q63', 'q64', 'q65', 'q66', 'q67', 'q68', 'q69', 'q70',
            'q71', 'q72', 'q73', 'q74', 'q75', 'q76', 'q77', 'q78', 'q79', 'q80',
            'q81', 'q82', 'q83', 'q84', 'q85', 'q86', 'q87', 'q88', 'q89', 'q90',
            'q91', 'q92', 'q93', 'q94', 'q95', 'q96', 'q97', 'q98', 'q99'
        ]
        if query_list is not None:
            query_set = set(query_list)
            if not query_set.issubset(self.QUERY_REGISTRY):
                unsupported_queries = query_set - set(self.QUERY_REGISTRY)
                raise ValueError(f"Query list contains unsupported queries: {unsupported_queries}. Supported queries: {self.QUERY_REGISTRY}.")
            self.query_list = query_list
        else:
            self.query_list = self.QUERY_REGISTRY

        self.benchmark_impl_class = next(
            (benchmark_impl for base_engine, benchmark_impl in self.BENCHMARK_IMPL_REGISTRY.items() if isinstance(engine, base_engine)),
            None
        )
        self.timer = timer

        if self.benchmark_impl_class is None:
            raise ValueError(
                f"No benchmark implementation registered for engine type: {type(engine).__name__} "
                f"in benchmark '{self.__class__.__name__}'."
            )
        
        self.storage_paths = {
            "source_data_mount_path": tpcds_parquet_mount_path,
            "source_data_abfss_path": tpcds_parquet_abfss_path,
        }
        self.engine = engine
        self.scenario_name = scenario_name
        self.benchmark_impl = self.benchmark_impl_class(
            self.storage_paths,
            self.engine
        )

    def run(self, mode: str = 'light'):

        match mode:
            case 'load':
                self._run_load_test()
            case 'query':
                self._run_query_test()
            case 'power_test':
                raise NotImplementedError("Power test mode is not implemented yet.")
            case _:
                raise ValueError(f"Unknown mode '{mode}'. Supported: {self.MODE_REGISTRY}.")
            
        results = self.post_results()
        return results

    def _run_load_test(self):
        self.benchmark_impl._prepare_schema() #TBD
        with self.timer('Loading TPCDS Tables', self.benchmark_impl):
            # TBD: Add test_item logging
            for table_name in self.TABLE_REGISTRY:
                self.benchmark_impl.load_parquet_to_delta(table_name) #TBD

    def _run_query_test(self):
        with self.timer('Loading TPCDS Tables', self.benchmark_impl):
            # TBD: Add test_item logging
            for query_name in self.query_list:

                with importlib.resources.path('lakebench.benchmarks.tpcds.resources.queries', f'{query_name}.sql') as query_path:
                    with open(query_path, 'r') as query_file:
                        query = query_file.read()

                self.benchmark_impl.run_query(query) #TBD

    def _run_power_test(self):
        self._run_load_test()
        self._run_query_test()

    def post_results(self):
        result_array = []
        for phase, duration_ms in self.timer.results:
            result_array.append({
                "phase": phase,
                "duration_sec": duration_ms / 1000,  # Convert ms to seconds
                "duration_ms": duration_ms,
                "engine": type(self.engine).__name__,
                "scenario": self.scenario_name,
                "cores": self.engine.get_total_cores()
            })

        if self.save_results:
            if self.result_abfss_path is None:
                raise ValueError("result_abfss_path must be provided if save_results is True.")
            else:
                self.engine.append_array_to_delta(self.result_abfss_path, result_array)

        self.timer.clear_results()
        return result_array