import sys
import pandas as pd


if len(sys.argv) != 4 or not sys.argv[3].startswith('--queues='):
    print("Usage: python ./filter-by-queue <input_csv> <output_csv> --queues=a,b,c...")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]
queues = [int(q) for q in sys.argv[3].replace('--queues=', '').split(',')]

df = pd.read_csv(input_csv)

df['queue-sys-id'] = df['queue-sys-id'].astype(int)

filtered = df[df['queue-sys-id'].isin(queues)]
filtered.to_csv(output_csv, index=False)

