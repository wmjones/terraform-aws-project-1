import pandas as pd
import numpy as np

import boto3
import sagemaker
import joblib

from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.preprocessing import Binarizer, StandardScaler, OneHotEncoder

import argparse


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()