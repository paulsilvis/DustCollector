import pandas as pd
from tabulate import tabulate

df = pd.read_excel("IOBitAssignments.ods", engine="odf")
print(tabulate(df, headers="keys", tablefmt="github"))

