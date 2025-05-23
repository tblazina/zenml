# Original License:
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# New License:
#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
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

from typing import TYPE_CHECKING, Any

from zenml.enums import OrchestratorFlavor
from zenml.integrations.kubeflow.orchestrators.kubeflow_orchestrator import (
    KubeflowOrchestrator,
)
from zenml.logger import get_logger
from zenml.stack import Stack

# from zenml.stack.stack_component_class_registry import (
#     register_stack_component_class,
# )

# from google.cloud import aiplatform
# from google.cloud.aiplatform import pipeline_jobs


if TYPE_CHECKING:
    from zenml.pipelines.base_pipeline import BasePipeline
    from zenml.runtime_configuration import RuntimeConfiguration


logger = get_logger(__name__)


# @register_stack_component_class(
#     component_type=StackComponentType.ORCHESTRATOR,
#     component_flavor=OrchestratorFlavor.VERTEX,
# )
class VertexOrchestrator(KubeflowOrchestrator):
    """Orchestrator responsible for running pipelines on Vertex AI."""

    supports_local_execution = False
    supports_remote_execution = True

    @property
    def flavor(self) -> OrchestratorFlavor:
        """The orchestrator flavor."""
        return OrchestratorFlavor.VERTEX

    def run_pipeline(
        self,
        pipeline: "BasePipeline",
        stack: "Stack",
        runtime_configuration: "RuntimeConfiguration",
    ) -> Any:
        """Runs a pipeline on Vertex AI using the Kubeflow orchestrator."""
        raise NotImplementedError("Vertex AI orchestration is coming soon!")
        # super().run_pipeline(pipeline, stack, runtime_configuration)

        # aiplatform.init(
        #     project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_REGION
        # )

        # job = pipeline_jobs.PipelineJob(
        #     template_path=PIPELINE_DEFINITION_FILE, display_name=PIPELINE_NAME
        # )
        # job.submit()
