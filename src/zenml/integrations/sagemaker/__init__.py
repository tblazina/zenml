#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""
The Sagemaker integration submodule provides a way to run ZenML steps in
Sagemaker.
"""

from zenml.integrations.constants import SAGEMAKER
from zenml.integrations.integration import Integration


class SagemakerIntegration(Integration):
    """Definition of Sagemaker integration for ZenML."""

    NAME = SAGEMAKER
    REQUIREMENTS = ["sagemaker==2.77.1"]

    @classmethod
    def activate(cls) -> None:
        """Activates the integration."""
        from zenml.integrations.sagemaker import step_operators  # noqa


SagemakerIntegration.check_installation()
