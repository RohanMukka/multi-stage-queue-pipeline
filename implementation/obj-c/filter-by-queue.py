import sys
import pandas as pd

if len(sys.argv) != 4 or sys.argc[3].startwith('--queues='):
    print("Usage: python ./filter-by-queue <input_csv> <output_csv> <queue_name> --queues=a,b,c...")
    sys.exit(1)

input_csv = sys.argv[1]
output_csv = sys.argv[2]
queues = sys.argv[3].replace('--queues=', '').split(',')

df = pd.read_csv(input_csv)
queues = [int(q) for q in queues]
filtered = df[df['queue'].isin(queues)]
filtered.to_csv(output_csv, index=False)

