# Copyright 2019, OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
This module serves as an example to integrate with flask, using
the requests library to perform downstream requests
"""
import flask
import pkg_resources
import requests

import opentelemetry.ext.http_requests
from opentelemetry import trace
from opentelemetry.ext.flask import instrument_app
from opentelemetry.sdk.trace import TracerProvider


def configure_opentelemetry(flask_app: flask.Flask):
    """Configure a flask application to use OpenTelemetry.

    This activates the specific components:

    * sets tracer to the SDK's Tracer
    * enables requests integration on the Tracer
    * uses a WSGI middleware to enable configuration

    TODO:

    * processors?
    * exporters?
    """
    # Start by configuring all objects required to ensure
    # a complete end to end workflow.
    # The preferred implementation of these objects must be set,
    # as the opentelemetry-api defines the interface with a no-op
    # implementation.
    trace.set_preferred_tracer_provider_implementation(
        lambda _: TracerProvider()
    )

    # Next, we need to configure how the values that are used by
    # traces and metrics are propagated (such as what specific headers
    # carry this value).
    # Integrations are the glue that binds the OpenTelemetry API
    # and the frameworks and libraries that are used together, automatically
    # creating Spans and propagating context as appropriate.
    opentelemetry.ext.http_requests.enable(trace.tracer_provider())
    instrument_app(flask_app)


app = flask.Flask(__name__)


@app.route("/")
def hello():
    # emit a trace that measures how long the
    # sleep takes
    version = pkg_resources.get_distribution(
        "opentelemetry-example-app"
    ).version
    tracer = trace.get_tracer(__name__, version)
    with tracer.start_as_current_span("example-request"):
        requests.get("http://www.example.com")
    return "hello"


configure_opentelemetry(app)
