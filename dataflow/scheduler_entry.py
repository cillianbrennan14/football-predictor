from core.db import init_schema
from dataflow.etl import run_fetch_and_load

def main():
    init_schema()
    run_fetch_and_load()

if __name__ == "__main__":
    main()
