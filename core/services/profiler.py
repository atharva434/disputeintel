import pandas as pd

class DataProfilingService:
    def profile(self, file_path):
        """
        Generates summary statistics for the given dataset.
        """
        try:
            df = pd.read_csv(file_path)
            
            summary = {
                "rows": len(df),
                "columns": list(df.columns),
                "missing_values": df.isnull().sum().to_dict(),
                "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "numeric_desc": df.describe().to_dict()
            }
            return summary
        except Exception as e:
            return {"error": str(e)}
