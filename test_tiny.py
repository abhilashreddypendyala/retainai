import pandas as pd
from backend.pipeline.pipeline import run_dataset_intelligence
import traceback

print("Loading tiny sample...")
df = pd.read_csv('tiny.csv')
print(f'Running with {len(df)} rows')
try:
    res = run_dataset_intelligence(df)
    print('Success!')
except Exception as e:
    print('Error!')
    traceback.print_exc()
