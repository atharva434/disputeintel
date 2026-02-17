class InsightGeneratorService:
    def generate(self, profiling_data, anomaly_data):
        """
        Generates text-based insights based on profiling and anomaly data.
        """
        insights = []
        
        # Example rule-based insights
        if "rows" in profiling_data:
            insights.append(f"The dataset contains {profiling_data['rows']} rows.")
            
        if anomaly_data:
            insights.append(f"Detected anomalies in {len(anomaly_data)} columns.")
            
        return insights
