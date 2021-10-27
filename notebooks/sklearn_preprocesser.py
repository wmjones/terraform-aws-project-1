import pandas as pd
import numpy as np

import boto3
import sagemaker
import joblib

from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.preprocessing import Binarizer, StandardScaler, OneHotEncoder

import argparse


bucket = "wyatt-datalake"
prefix = "terraform-aws-project-1"


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
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
    
    df = pd.read_csv("s3://wyatt-datalake/data/terraform-aws-project-1/vehicles.csv", dtype=df_dtypes, usecols=list(df_dtypes.keys()))
    
    features = df.drop("price", axis=1).values
    labels = df["price"].values
    np.random.seed(0)
    
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
    
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels, test_size=0.2
    )
    X_val, X_test, y_val, y_test = train_test_split(
        test_features, test_labels, test_size=0.5
    )

    buf = io.BytesIO()
    smac.write_numpy_to_dense_tensor(buf, X_train, y_train)
    buf.seek(0)
    
    # for split in ["train", "val", "test"]:

    ###Uploading training data
    #Filename for training data we are uploading to S3 
    key = 'linear-train-data'
    #Upload training data to S3
    boto3.resource('s3').Bucket(bucket).Object(os.path.join(prefix, 'train', key)).upload_fileobj(buf)
    s3_train_data = 's3://{}/{}/train/{}'.format(bucket, prefix, key)
    print('uploaded training data location: {}'.format(s3_train_data))

    ###Uploading test data
    buf = io.BytesIO() # create an in-memory byte array (buf is a buffer I will be writing to)
    smac.write_numpy_to_dense_tensor(buf, X_test, y_test)
    buf.seek(0)

    #Sub-folder for test data
    key = 'linear-test-data'
    boto3.resource('s3').Bucket(bucket).Object(os.path.join(prefix, 'test', key)).upload_fileobj(buf)
    s3_test_data = 's3://{}/{}/test/{}'.format(bucket, prefix, key)
    print('uploaded training data location: {}'.format(s3_test_data))
    
    ###Uploading val data
    buf = io.BytesIO() # create an in-memory byte array (buf is a buffer I will be writing to)
    smac.write_numpy_to_dense_tensor(buf, X_val, y_val)
    buf.seek(0)
    
    #Sub-folder for val data
    key = 'linear-val-data'
    boto3.resource('s3').Bucket(bucket).Object(os.path.join(prefix, 'val', key)).upload_fileobj(buf)
    s3_val_data = 's3://{}/{}/test/{}'.format(bucket, prefix, key)
    print('uploaded training data location: {}'.format(s3_val_data))

    ###Model Artifacts
    output_location = 's3://{}/{}/output'.format(bucket, prefix)
    print('Training artifacts will be uploaded to: {}'.format(output_location))
