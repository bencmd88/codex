"""
Data processing automation for business products.
"""
import pandas as pd
import numpy as np
import os
import json
import csv
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging

from .core import AutomationTask, logger

class DataImportTask(AutomationTask):
    """Task for importing data from various sources"""
    
    def __init__(self, name: str, source_type: str, source_path: str, **kwargs):
        """
        Initialize a data import task
        
        Args:
            name: Task name
            source_type: Type of data source (csv, excel, json, etc.)
            source_path: Path to the data source
            **kwargs: Additional arguments for the specific import function
        """
        super().__init__(name, f"Import data from {source_type} file: {source_path}")
        self.source_type = source_type.lower()
        self.source_path = source_path
        self.import_args = kwargs
    
    def _execute(self, *args, **kwargs) -> pd.DataFrame:
        """Import data from the specified source"""
        if not os.path.exists(self.source_path):
            raise FileNotFoundError(f"Source file not found: {self.source_path}")
        
        if self.source_type == 'csv':
            df = pd.read_csv(self.source_path, **self.import_args)
        elif self.source_type == 'excel' or self.source_type == 'xlsx':
            df = pd.read_excel(self.source_path, **self.import_args)
        elif self.source_type == 'json':
            df = pd.read_json(self.source_path, **self.import_args)
        elif self.source_type == 'parquet':
            df = pd.read_parquet(self.source_path, **self.import_args)
        elif self.source_type == 'sql':
            # For SQL, source_path is the query and we need a connection string
            conn_string = self.import_args.pop('connection_string', None)
            if not conn_string:
                raise ValueError("connection_string is required for SQL imports")
            import sqlalchemy
            engine = sqlalchemy.create_engine(conn_string)
            df = pd.read_sql(self.source_path, engine, **self.import_args)
        else:
            raise ValueError(f"Unsupported source type: {self.source_type}")
        
        logger.info(f"Imported {len(df)} rows from {self.source_path}")
        return df

class DataTransformTask(AutomationTask):
    """Task for transforming data"""
    
    def __init__(self, name: str, transform_function, description: str = ""):
        """
        Initialize a data transformation task
        
        Args:
            name: Task name
            transform_function: Function that takes a DataFrame and returns a transformed DataFrame
            description: Task description
        """
        super().__init__(name, description or "Transform data using custom function")
        self.transform_function = transform_function
    
    def _execute(self, data: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        """Transform the input data"""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        result = self.transform_function(data, *args, **kwargs)
        
        if not isinstance(result, pd.DataFrame):
            raise TypeError("Transform function must return a pandas DataFrame")
        
        logger.info(f"Transformed data: {len(data)} rows in, {len(result)} rows out")
        return result

class DataExportTask(AutomationTask):
    """Task for exporting data to various destinations"""
    
    def __init__(self, name: str, destination_type: str, destination_path: str, **kwargs):
        """
        Initialize a data export task
        
        Args:
            name: Task name
            destination_type: Type of data destination (csv, excel, json, etc.)
            destination_path: Path to the data destination
            **kwargs: Additional arguments for the specific export function
        """
        super().__init__(name, f"Export data to {destination_type} file: {destination_path}")
        self.destination_type = destination_type.lower()
        self.destination_path = destination_path
        self.export_args = kwargs
    
    def _execute(self, data: pd.DataFrame, *args, **kwargs) -> str:
        """Export data to the specified destination"""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(self.destination_path)), exist_ok=True)
        
        if self.destination_type == 'csv':
            data.to_csv(self.destination_path, **self.export_args)
        elif self.destination_type == 'excel' or self.destination_type == 'xlsx':
            data.to_excel(self.destination_path, **self.export_args)
        elif self.destination_type == 'json':
            data.to_json(self.destination_path, **self.export_args)
        elif self.destination_type == 'parquet':
            data.to_parquet(self.destination_path, **self.export_args)
        elif self.destination_type == 'sql':
            # For SQL, destination_path is the table name and we need a connection string
            conn_string = self.export_args.pop('connection_string', None)
            if not conn_string:
                raise ValueError("connection_string is required for SQL exports")
            import sqlalchemy
            engine = sqlalchemy.create_engine(conn_string)
            data.to_sql(self.destination_path, engine, **self.export_args)
        else:
            raise ValueError(f"Unsupported destination type: {self.destination_type}")
        
        logger.info(f"Exported {len(data)} rows to {self.destination_path}")
        return self.destination_path

class DataAnalysisTask(AutomationTask):
    """Task for analyzing data"""
    
    def __init__(self, name: str, analysis_type: str, **kwargs):
        """
        Initialize a data analysis task
        
        Args:
            name: Task name
            analysis_type: Type of analysis (summary, correlation, etc.)
            **kwargs: Additional arguments for the specific analysis
        """
        super().__init__(name, f"Perform {analysis_type} analysis on data")
        self.analysis_type = analysis_type.lower()
        self.analysis_args = kwargs
    
    def _execute(self, data: pd.DataFrame, *args, **kwargs) -> Dict[str, Any]:
        """Analyze the input data"""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Input must be a pandas DataFrame")
        
        results = {}
        
        if self.analysis_type == 'summary':
            results['describe'] = data.describe().to_dict()
            results['info'] = {
                'shape': data.shape,
                'columns': list(data.columns),
                'dtypes': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'missing_values': data.isna().sum().to_dict()
            }
        
        elif self.analysis_type == 'correlation':
            # Get columns that are numeric
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                results['correlation'] = data[numeric_cols].corr().to_dict()
            else:
                results['correlation'] = {}
                logger.warning("Not enough numeric columns for correlation analysis")
        
        elif self.analysis_type == 'custom':
            analysis_func = self.analysis_args.get('analysis_function')
            if not analysis_func:
                raise ValueError("analysis_function is required for custom analysis")
            results = analysis_func(data, **self.analysis_args)
        
        else:
            raise ValueError(f"Unsupported analysis type: {self.analysis_type}")
        
        logger.info(f"Completed {self.analysis_type} analysis on data")
        return results