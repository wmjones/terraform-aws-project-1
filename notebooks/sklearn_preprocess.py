import pandas as pd
import numpy as np

import boto3
# import sagemaker
# import joblib

from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.preprocessing import Binarizer, StandardScaler, OneHotEncoder
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

import io
import sagemaker.amazon.common as smac

import argparse
import logging
import pathlib


bucket = "wyatt-datalake"
prefix = "terraform-aws-project-1"
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


if __name__ == '__main__':
    logger.info("Starting preprocessing.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-data", type=str, required=True)
    args = parser.parse_args()
    base_dir = "/opt/ml/processing"
    pathlib.Path("{}/data".format(base_dir)).mkdir(parents=True, exist_ok=True)
    pathlib.Path("{}/data/input".format(base_dir)).mkdir(exist_ok=True)
    
    input_data = args.input_data
    print(input_data)

    logger.info("Reading downloaded data.")
    df_dtypes = {
        "price": np.float32,
        "year": np.float16,
        "manufacturer": "category",
        "model": "category",
        "condition": "category",
        "cylinders": "category",
        "fuel": "category",
        "title_status": "category",
        "size": "category",
        "odometer": "category",
        "transmission": "category",
        "drive": "category",
        "type": "category",
        "state": "category",
        "paint_color": "category"
    }
    df = pd.read_csv(input_data, dtype=df_dtypes, usecols=list(df_dtypes.keys()), engine='python')
    features = df.drop("price", axis=1).values
    labels = df["price"].values
    np.random.seed(0)

    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_test, y_test, test_size=0.5
    )
    
    def foo(split, features, labels):
        numeric_transformer = make_pipeline(
            SimpleImputer(strategy='median'),
            StandardScaler())

        categorical_transformer = make_pipeline(
            SimpleImputer(strategy='constant', fill_value='missing'),
            OneHotEncoder(handle_unknown='ignore'))

        preprocessor = ColumnTransformer(transformers=[
                ("num", numeric_transformer, make_column_selector(dtype_exclude="category")),
                ("cat", categorical_transformer, make_column_selector(dtype_include="category"))])
        features = preprocessor.fit_transform(df.drop("price", axis=1))
        features = features.astype(np.float32)

        buf = io.BytesIO()
        smac.write_spmatrix_to_sparse_tensor(buf, features, target)
        buf.seek(0)

        #Filename for training data we are uploading to S3 
        key = 'linear-data'
        #Upload training data to S3
        boto3.resource('s3').Bucket(bucket).Object(os.path.join(prefix, split, key)).upload_fileobj(buf)
        s3_split_data = 's3://{}/{}/{}/{}'.format(bucket, prefix, split, key)
        print('uploaded {} data location: {}'.format(split, s3_split_data))

    foo('train', X_train, y_train)
    foo('test', X_test, y_test)
    foo('val', X_val, y_val)

    ###Model Artifacts
    output_location = 's3://{}/{}/output'.format(bucket, prefix)
    print('Model Artifacts will be uploaded to: {}'.format(output_location))

