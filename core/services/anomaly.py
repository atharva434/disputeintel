import pandas as pd
import numpy as np

class AnomalyDetectionService:
    def detect(self, file_path):
        """
        Detects basic anomalies (outliers) in numeric columns.
        """
        try:
            df = pd.read_csv(file_path)
            anomalies = {}
            
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            
            for col in numeric_cols:
                # Simple IQR based outlier detection
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))]
                
                if not outliers.empty:
                    anomalies[col] = {
                        "count": len(outliers),
                        "indices": outliers.index.tolist(),
                        "values": outliers[col].tolist()
                    }
                    
            return anomalies
        except Exception as e:
            return {"error": str(e)}
