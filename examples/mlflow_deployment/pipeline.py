#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import os

import mlflow  # type: ignore [import]
import numpy as np  # type: ignore [import]
import pandas as pd  # type: ignore [import]
import requests  # type: ignore [import]
import tensorflow as tf  # type: ignore [import]

from zenml.integrations.mlflow.mlflow_step_decorator import enable_mlflow
from zenml.integrations.mlflow.services import MLFlowDeploymentService
from zenml.integrations.mlflow.steps import mlflow_deployer_step
from zenml.pipelines import pipeline
from zenml.services import load_last_service_from_step
from zenml.steps import BaseStepConfig, Output, StepContext, step

# Path to a pip requirements file that contains requirements necessary to run
# the pipeline
requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")


class TrainerConfig(BaseStepConfig):
    """Trainer params"""

    epochs: int = 1
    lr: float = 0.001


@step
def importer_mnist() -> Output(
    x_train=np.ndarray, y_train=np.ndarray, x_test=np.ndarray, y_test=np.ndarray
):
    """Download the MNIST data store it as an artifact"""
    (x_train, y_train), (
        x_test,
        y_test,
    ) = tf.keras.datasets.mnist.load_data()
    return x_train, y_train, x_test, y_test


@step
def normalizer(
    x_train: np.ndarray, x_test: np.ndarray
) -> Output(x_train_normed=np.ndarray, x_test_normed=np.ndarray):
    """Normalize the values for all the images so they are between 0 and 1"""
    x_train_normed = x_train / 255.0
    x_test_normed = x_test / 255.0
    return x_train_normed, x_test_normed


# Define the step and enable MLflow (n.b. order of decorators is important here)
@enable_mlflow
@step
def tf_trainer(
    config: TrainerConfig,
    x_train: np.ndarray,
    y_train: np.ndarray,
) -> tf.keras.Model:
    """Train a neural net from scratch to recognize MNIST digits return our
    model or the learner"""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(10),
        ]
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(config.lr),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    mlflow.tensorflow.autolog()
    model.fit(
        x_train,
        y_train,
        epochs=config.epochs,
    )

    # write model
    return model


# Define the step and enable MLflow (n.b. order of decorators is important here)
@enable_mlflow
@step
def tf_evaluator(
    x_test: np.ndarray,
    y_test: np.ndarray,
    model: tf.keras.Model,
) -> float:
    """Calculate the loss for the model for each epoch in a graph"""

    _, test_acc = model.evaluate(x_test, y_test, verbose=2)
    mlflow.log_metric("val_accuracy", test_acc)
    return test_acc


class DeploymentTriggerConfig(BaseStepConfig):
    """Parameters that are used to trigger the deployment"""

    min_accuracy: float


@step
def deployment_trigger(
    accuracy: float,
    config: DeploymentTriggerConfig,
) -> bool:
    """Implements a simple model deployment trigger that looks at the
    input model accuracy and decides if it is good enough to deploy"""

    return accuracy > config.min_accuracy


model_deployer = mlflow_deployer_step(name="model_deployer")


class MLFlowDeploymentLoaderStepConfig(BaseStepConfig):
    """MLflow deployment getter configuration

    Attributes:
        pipeline_name: name of the pipeline that deployed the MLflow prediction
            server
        step_name: the name of the step that deployed the MLflow prediction
            server
        running: when this flag is set, the step only returns a running service
    """

    pipeline_name: str
    step_name: str
    running: bool = True


@step(enable_cache=False)
def prediction_service_loader(
    config: MLFlowDeploymentLoaderStepConfig, context: StepContext
) -> MLFlowDeploymentService:
    """Get the prediction service started by the deployment pipeline"""

    service = load_last_service_from_step(
        pipeline_name=config.pipeline_name,
        step_name=config.step_name,
        step_context=context,
        running=config.running,
    )
    if not service:
        raise RuntimeError(
            f"No MLflow prediction service deployed by the "
            f"{config.step_name} step in the {config.pipeline_name} pipeline "
            f"is currently running."
        )

    return service


def get_data_from_api():
    url = (
        "https://storage.googleapis.com/zenml-public-bucket/mnist"
        "/mnist_handwritten_test.json"
    )

    df = pd.DataFrame(requests.get(url).json())
    data = df["image"].map(lambda x: np.array(x)).values
    data = np.array([x.reshape(28, 28) for x in data])
    return data


@step(enable_cache=False)
def dynamic_importer() -> Output(data=np.ndarray):
    """Downloads the latest data from a mock API."""
    data = get_data_from_api()
    return data


@step
def predictor(
    service: MLFlowDeploymentService,
    data: np.ndarray,
) -> Output(predictions=np.ndarray):
    """Run a inference request against a prediction service"""

    service.start(timeout=10)  # should be a NOP if already started
    prediction = service.predict(data)
    prediction = prediction.argmax(axis=-1)

    return prediction


@pipeline(enable_cache=True, requirements_file=requirements_file)
def continuous_deployment_pipeline(
    importer,
    normalizer,
    trainer,
    evaluator,
    deployment_trigger,
    model_deployer,
):
    # Link all the steps artifacts together
    x_train, y_train, x_test, y_test = importer()
    x_trained_normed, x_test_normed = normalizer(x_train=x_train, x_test=x_test)
    model = trainer(x_train=x_trained_normed, y_train=y_train)
    accuracy = evaluator(x_test=x_test_normed, y_test=y_test, model=model)
    deployment_decision = deployment_trigger(accuracy=accuracy)
    model_deployer(deployment_decision)


@pipeline(enable_cache=True, requirements_file=requirements_file)
def inference_pipeline(
    dynamic_importer,
    prediction_service_loader,
    predictor,
):
    # Link all the steps artifacts together
    batch_data = dynamic_importer()
    model_deployment_service = prediction_service_loader()
    predictor(model_deployment_service, batch_data)
