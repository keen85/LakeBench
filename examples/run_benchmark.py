##### NAME IDEAS
name = "BenchFactory"
name = "LakeBench"
name = "BenchLake"
#####


from lakebench.engines.fabric_spark import FabricSpark
from lakebench.benchmarks.elt_bench import ELTBench

engine = FabricSpark(
    lakehouse_workspace_name = 'mcole_scenario_repl', 
    lakehouse_name = 'mcole_benchmarks', 
    lakehouse_schema_name = 'spark_atomic_elt_100_8core',
    spark_measure_telemetry = False
)

benchmark = ELTBench(
    engine=engine,
    scenario_name="4vCores",
    tpcds_parquet_abfss_path='abfss://........./Files/tpcds/source/sf1_parquet',
    save_results=False,
    result_abfss_path='abfss://......../Tables/dbo/results'
    )
benchmark.run(mode="light")

###################
from lakebench.engines.polars import Polars
from lakebench.benchmarks.elt_bench import ELTBench

engine = Polars( 
    delta_abfss_schema_path = 'abfss://.........../Tables/polars_atomic_elt_100_8core'
)

benchmark = ELTBench(
    engine=engine,
    scenario_name="4vCores",
    tpcds_parquet_abfss_path='abfss://........./Files/tpcds/source/sf1_parquet',
    save_results=False,
    result_abfss_path='abfss://........../Tables/dbo/results'
    )
benchmark.run(mode="light")

###################
from lakebench.engines.duckdb import DuckDB
from lakebench.benchmarks.elt_bench import ELTBench

engine = DuckDB( 
    delta_abfss_schema_path = 'abfss://.........../Tables/polars_atomic_elt_100_8core'
)

benchmark = ELTBench(
    engine=engine,
    scenario_name="4vCores",
    tpcds_parquet_abfss_path='abfss://........./Files/tpcds/source/sf1_parquet',
    save_results=False,
    result_abfss_path='abfss://............./Tables/dbo/results'
    )
benchmark.run(mode="light")


###################
from lakebench.engines.daft import Daft
from lakebench.benchmarks.elt_bench import ELTBench

engine = Daft( 
    delta_abfss_schema_path = 'abfss://............./Tables/polars_atomic_elt_100_8core',
    delta_mount_schema_path = '/lakehouse/default/Tables/polars_atomic_elt_100_8core'
)

benchmark = ELTBench(
    engine=engine,
    scenario_name="4vCores",
    tpcds_parquet_mount_path='/lakehouse/default/Files/tpcds/source/sf1_parquet',
    save_results=False,
    result_abfss_path='abfss://.............../Tables/dbo/results'
    )
benchmark.run(mode="light")