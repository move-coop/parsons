from __future__ import annotations
from typing import Callable, List, Optional, Union, Dict, TypeAlias
from abc import ABC, abstractmethod
from enum import Enum
import os
import functools
from parsons import Table
import requests
from pathlib import Path
import shutil
from prefect import task, flow

### Our goal is to convert this to use Prefect and Dask instead of Parsons Tables.
### Here is an example blog post we are going to base this off of:

# ETL Pipelines with Prefect

# Prefect is a platform for automating data workflows. Data engineers and data scientists can build, test and deploy production pipelines without worrying about all of the "negative engineering" aspects of production. For example, Prefect makes it easy to deploy a workflow that runs on a complicated schedule, requires task retries in the event of failures, and sends notifications when certain tasks are complete. Prefect was built on top of Dask, and relies on Dask to schedule and manage the execution of a Prefect workflow in a distributed environment.

# This example demonstrates running a Prefect ETL Flow on Dask which ultimately creates a GIF. While this is a somewhat unconventional use case of Prefect, we're no strangers to unconventional use cases.

# In the world of workflow engines, Prefect supports many unique features; in this particular example we will see:

#     parametrization of workflows
#     dynamic runtime "mapping" of workflow tasks
#     customizable execution logic

# You wouldn't get this from any other engine.

# Contents

#     Description of goal
#     Building our Flow
#         Extract
#         Transform
#         Load
#         Putting the pieces together
#     Running our Flow on Dask
#     Watching our GIF

# Goal

# To demonstrate how Prefect and Dask work together, we are going to build and execute a standard "Extract / Transform / Load" (ETL) workflow for processing some basic image data. Most ETL workflows involve a scheduled migration of data from one database to another. In our case, we will be moving data from a file located at a known URL to our local hard disk, converting the individual file into a series of frames, and compiling those frames into a GIF. The URL references a file containing raw bytes such as:

# b"""aÙw˜  ≠•∆≠≠ﬁ#!≠≠÷≠•Ω≠úΩ••µú•µîúµ•úΩ••Ω3&µ•Ω!µ≠∆≠•¥4(%µú∑≠≠Œ≠î≠≠≠∆≠îµúî≠úîµE5.≠ú≠≠•Œµµﬁ••∆•≠ŒµµŒúúΩ62&)1&623µ•∆Ωµ÷úî•ßjxΩΩÁú•Ωµ≠Œ••≠ú•≠Ω≠∆≠µÁâUV≠µ‹ΩµŒîî•NC5µ≠Ÿôãô•î•µ•µîú≠#VHCuhl≠≠ΩôchâRIoc]™≠Á≠î•™ú»öis•ú•f7,íYfL9?îî≠≠•÷∑ò™gWVxGEΩ≠–))1qB5µ≠Ω81R,´tÜñWV!HCDBB5;5?"""

# The steps of our workflow will be as follows:

#     Extract: pull the data file from a URL (specified by a Parameter) to disk
#     Transform: split the file into multiple files, each corresponding to a single frame
#     Load: Store each frame individually, and compile the frames together into a GIF

# Once we have built our Flow, we can execute it with different values for the Parameter or even run it on a nightly schedule.

# NOTE: If we planned on executing this Flow in a truly distributed environment, writing the images to the local filesystem would not be appropriate. We would instead use an external datastore such as Google Cloud Storage, or a proper database.
# Extract

# First, we will define our tasks for extracting the image data file from a given URL and saving it to a given file location. To do so, we will utilize two methods for creating Prefect Tasks:

#     the task decorator for converting any Python function into a task
#     a pre-written, configurable Task from the Prefect "Task Library" which helps us abstract some standard boilerplate

# Additionally, we will utilize the following Prefect concepts:

#     a Prefect signal for marking this task and its downstream depedencies as successfully "Skipped" if the file is already present in our local filesystem
#     retry semantics: if, for whatever reason, our curl command fails to connect, we want it to retry up to 2 times with a 10 second delay. This way, if we run this workflow on a schedule we won't need to concern ourselves with temporary intermittent connection issues.

# Right now we are simply defining our individual tasks - we won't actually set up our dependency structure until we create the full Flow.

# import datetime
# import os

# import prefect
# from prefect import task
# from prefect.engine.signals import SKIP
# from prefect.tasks.shell import ShellTask


# @task
# def curl_cmd(url: str, fname: str) -> str:
#     """
#     The curl command we wish to execute.
#     """
#     if os.path.exists(fname):
#         raise SKIP("Image data file already exists.")
#     return "curl -fL -o {fname} {url}".format(fname=fname, url=url)


# # ShellTask is a task from the Task library which will execute a given command in a subprocess
# # and fail if the command returns a non-zero exit code

# download = ShellTask(name="curl_task", max_retries=2, retry_delay=datetime.timedelta(seconds=10))

# Transform

# Next up, we need to define our task which loads the image data file and splits it into multiple frames. In this case, each frame is delimited by 4 newlines. Note that, in the event the previous two tasks are "Skipped", the default behavior in Prefect is to skip downstream dependencies as well. However, as with most things in Prefect, this behavior is customizable. In this case, we want this task to run regardless of whether the upstreams skipped or not, so we set the skip_on_upstream_skip flag to False.

# @task(skip_on_upstream_skip=False)
# def load_and_split(fname: str) -> list:
#     """
#     Loads image data file at `fname` and splits it into
#     multiple frames.  Returns a list of bytes, one element
#     for each frame.
#     """
#     with open(fname, "rb") as f:
#         images = f.read()

#     return [img for img in images.split(b"\n" * 4) if img]

# Load

# Finally, we want to write our frames to disk as well as combine the frames into a single GIF. In order to achieve this goal, we are going to utilize Prefect's task "mapping" feature which conveniently spawns new tasks in response to upstream outputs. In this case, we will write a single task for writing an image to disk, and "map" this task over all the image frames returned by load_and_split above! To infer which frame we are on, we look in prefect.context.

# Additionally, we can "reduce" over a mapped task - in this case, we will take the collection of mapped tasks and pass them into our combine_to_gif task for creating and saving our GIF.

# @task
# def write_to_disk(image: bytes) -> bytes:
#     """
#     Given a single image represented as bytes, writes the image
#     to the present working directory with a filename determined
#     by `map_index`.  Returns the image bytes.
#     """
#     frame_no = prefect.context.get("map_index")
#     with open("frame_{0:0=2d}.gif".format(frame_no), "wb") as f:
#         f.write(image)
#     return image

# import imageio
# from io import BytesIO


# @task
# def combine_to_gif(image_bytes: list) -> None:
#     """
#     Given a list of ordered images represented as bytes,
#     combines them into a single GIF stored in the present working directory.
#     """
#     images = [imageio.imread(BytesIO(image)) for image in image_bytes]
#     imageio.mimsave('./clip.gif', images)

# Build the Flow

# Finally, we need to put our tasks together into a Prefect "Flow". Similar to Dask's delayed interface, all computation is deferred and no Task code will be executed in this step. Because Prefect maintains a stricter contract between tasks and additionally needs the ability to run in non-Dask execution environments, the mechanism for deferring execution is independent of Dask.

# In addition to the tasks we have already defined, we introduce two "Parameters" for specifying the URL and local file location of our data. At runtime, we can optionally override these tasks to return different values.

# from prefect import Parameter, Flow


# DATA_URL = Parameter("DATA_URL",
#                      default="https://github.com/cicdw/image-data/blob/master/all-images.img?raw=true")

# DATA_FILE = Parameter("DATA_FILE", default="image-data.img")


# with Flow("Image ETL") as flow:

#     # Extract
#     command = curl_cmd(DATA_URL, DATA_FILE)
#     curl = download(command=command)

#     # Transform
#     # we use the `upstream_tasks` keyword to specify non-data dependencies
#     images = load_and_split(fname=DATA_FILE, upstream_tasks=[curl])

#     # Load
#     frames = write_to_disk.map(images)
#     result = combine_to_gif(frames)


# flow.visualize()

# Running the Flow on Dask

# Now we have built our Flow, independently of Dask. We could execute this Flow sequentially, Task after Task, but there is inherent parallelism in our mapping of the images to files that we want to exploit. Luckily, Dask makes this easy to achieve.

# First, we will start a local Dask cluster. Then, we will run our Flow against Prefect's DaskExecutor, which will submit each Task to our Dask cluster and use Dask's distributed scheduler for determining when and where each Task should run. Essentially, we built a Directed Acylic Graph (DAG) and are simply "submitting" that DAG to Dask for handling its execution in a distributed way.

# # start our Dask cluster
# from dask.distributed import Client


# client = Client(n_workers=4, threads_per_worker=1)

# # point Prefect's DaskExecutor to our Dask cluster

# from prefect.executors import DaskExecutor

# executor = DaskExecutor(address=client.scheduler.address)
# flow.run(executor=executor)

# Next Steps

# Now that we've built our workflow, what next? The interested reader should try to:

#     run the Flow again to see how the SKIP signal behaves
#     use different parameters for both the URL and the file location (Parameter values can be overriden by simply passing their names as keyword arguments to flow.run())
#     introduce a new Parameter for the filename of the final GIF
#     use Prefect's scheduler interface to run our workflow on a schedule

# Play

# Finally, let's watch our creation!

# from IPython.display import Image

# Image(filename="clip.gif", alt="Rick Daskley")


PipeResult = Enum("PipeResult", ["Unit", "Serial", "Parallel"])
StreamKey: TypeAlias = int
StreamsData: TypeAlias = Dict[StreamKey, Table]


class Logger(ABC):
    def __init__(self):
        self.pipe_offset = 0
        self.pipeline_offset = 0

    def setup(self):
        pass

    def next_pipe(self):
        self.pipe_offset += 1

    def next_pipeline(self):
        self.pipe_offset = 0
        self.pipeline_offset += 1

    @abstractmethod
    def log_data(self, data: Union[Table, StreamsData], pipe_name: str):
        pass


class CsvLogger(Logger):
    def __init__(self, dirname: str = "logging"):
        super().__init__()
        self.dirname = dirname

    def setup(self):
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def log_data(self, data: Table | StreamsData, pipe_name: str):
        if isinstance(data, Table):
            filename = f"{self.pipeline_offset}_{self.pipe_offset}_{pipe_name}.csv"
            data.to_csv(os.path.join(self.dirname, filename))
        else:
            for i in data.keys():
                self.log_data(data[i], f"{pipe_name}__stream_{i}")


class BreakpointLogger(Logger):
    def log_data(self, data: Table | StreamsData, pipe_name: str):
        breakpoint()


class Loggers(Logger):
    def __init__(self, *loggers: Logger):
        super().__init__()
        self.loggers = loggers

    def setup(self):
        super().setup()
        for logger in self.loggers:
            logger.setup()

    def next_pipe(self):
        super().next_pipe()
        for logger in self.loggers:
            logger.next_pipe()

    def next_pipeline(self):
        super().next_pipeline()
        for logger in self.loggers:
            logger.next_pipeline()

    def log_data(self, data: Table | StreamsData, pipe_name: str):
        for logger in self.loggers:
            logger.log_data(data, pipe_name)


class PipeBuilder:
    name: str
    func: Callable
    first_pipe: PipeBuilder
    next_pipe: Optional[PipeBuilder]
    input_type: PipeResult
    result_type: PipeResult

    def __init__(self, name, input_type, result_type, func: Callable) -> None:
        self.name = name
        self.func = func
        self.first_pipe = self
        self.next_pipe = None
        self.input_type = input_type
        self.result_type = result_type

    def __repr__(self) -> str:
        return f"{self.name} - {super().__repr__()}"

    def clean_copy(self) -> PipeBuilder:
        """Create a clean copy of this PipeBuilder."""
        return PipeBuilder(self.name, self.input_type, self.result_type, self.func)

    def is_connected(self) -> bool:
        return self.first_pipe != self or self.next_pipe is not None

    def __call__(self, next: PipeBuilder) -> PipeBuilder:
        if self.next_pipe is not None:
            raise RuntimeError(
                "Cannot chain from a pipe that has already been connected."
            )
        if self.result_type != next.input_type:
            raise RuntimeError(
                f"Cannot chain a {self.result_type} output pipe [{self.name}]"
                f" into a {next.input_type} input pipe [{next.name}]."
            )

        if not next.is_connected():
            next.first_pipe = self.first_pipe
            self.next_pipe = next
            return next
        else:
            pipe = next.first_pipe
            self.next_pipe = pipe
            pipe.first_pipe = self.first_pipe
            while pipe.next_pipe is not None:
                pipe = pipe.next_pipe
                pipe.first_pipe = self.first_pipe
            return pipe


class Pipeline:
    def __init__(self, name: str, final_pipe: PipeBuilder):
        self.name = name
        self.final_pipe = final_pipe

    # TODO: Figure out this return type
    def run(self, logger: Optional[Logger] = None):
        @flow(name=self.name)
        def run_flow():
            data: Optional[Union[Table, StreamsData]] = None
            pipe: Optional[PipeBuilder] = self.final_pipe.first_pipe

            if not pipe or pipe.input_type != PipeResult.Unit:
                raise RuntimeError(
                    "Must start Pipeline with a source pipeline. (Unit input type.)"
                )

            while pipe is not None:
                # TODO: Check the input type with the data type and throw errors if mismatch
                if pipe.input_type == PipeResult.Unit:
                    data = pipe.func()
                else:
                    data = pipe.func(data)

                if logger and data:
                    logger.log_data(data, pipe.name)
                    logger.next_pipe()

                pipe = pipe.next_pipe

            if data is None:
                raise RuntimeError("Lost data somehow. THIS SHOULD NEVER HAPPEN.")

            return data

        run_flow()

    def __str__(self) -> str:
        result = ""
        pipe = self.final_pipe.first_pipe
        while pipe:
            result += f"- {pipe.name}\n"
            pipe = pipe.next_pipe
        return result


class Dashboard:
    def __init__(self, *pipelines: Pipeline, logger: Optional[Logger] = None):
        self.pipelines = pipelines
        self.logger = logger

    def run(self):
        if self.logger:
            self.logger.setup()

        for p in self.pipelines:
            p.run(self.logger)

            if self.logger:
                self.logger.next_pipeline()

    def generate_report(self, filename: str):
        html_report = "<html><head><style>"
        html_report += "table {width: 100%; border-collapse: collapse;}"
        html_report += (
            "th, td {border: 1px solid black; text-align: center; padding: 10px;}"
        )
        html_report += "</style></head><body>"
        html_report += "<h2>Pipeline Report</h2>"
        html_report += "<table>"

        for pipeline in self.pipelines:
            html_report += "<tr>"
            pipe = pipeline.final_pipe.first_pipe
            while pipe:
                html_report += f"<td>{pipe.name}</td>"
                pipe = pipe.next_pipe
            html_report += "</tr>"

        html_report += "</table></body></html>"

        with open(filename, "w") as file:
            file.write(html_report)


def define_pipe(
    name: str,
    input_type: PipeResult = PipeResult.Serial,
    result_type: PipeResult = PipeResult.Serial,
    **task_args,
):
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> PipeBuilder:
            if input_type == PipeResult.Unit:

                @task(name=name, **task_args)
                def pipe_func_unit():
                    return func(*args, **kwargs)

                return PipeBuilder(name, input_type, result_type, pipe_func_unit)

            elif input_type == PipeResult.Parallel:

                def pipe_func_parallel(data: StreamsData):
                    return func(data, *args, **kwargs)

                return PipeBuilder(name, input_type, result_type, pipe_func_parallel)

            else:

                @task(name=name, **task_args)
                def pipe_func(data):
                    return func(data, *args, **kwargs)

                return PipeBuilder(name, input_type, result_type, pipe_func)

        return wrapper

    return decorator


@define_pipe("load_from_csv", input_type=PipeResult.Unit)
def load_from_csv(filename: str, **kwargs) -> Table:
    return Table.from_csv(filename, **kwargs)


@define_pipe("load_lotr_books", input_type=PipeResult.Unit)
def load_lotr_books_from_api() -> Table:
    # Set up the endpoint and headers
    url = "https://the-one-api.dev/v2/book"
    headers = {}

    # Make the request to the API
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises an HTTPError if the response was an error

    # Convert the JSON response into a Parsons Table
    books_json = response.json().get("docs", [])
    books_table = Table(books_json)

    return books_table


@define_pipe("convert")
def convert(data: Table, *args, **kwargs) -> Table:
    results = data.convert_column(*args, **kwargs)
    return results


@define_pipe("write_csv")
def write_csv(data: Table, csv_name: str) -> Table:
    data.to_csv(csv_name)
    return data


@define_pipe("filter_rows")
def filter_rows(data: Table, filters: Union[Callable, str, dict]) -> Table:
    if isinstance(filters, str) or isinstance(filters, Callable):
        results = data.select_rows(filters)
        return results
    else:

        def __select(row: dict) -> bool:
            for k, v in filters.items():
                if isinstance(v, Callable):
                    if not v(row[k]):
                        return False
                else:
                    if row[k] != v:
                        return False
            return True

        results = data.select_rows(__select)
        return results


@define_pipe("split_data", result_type=PipeResult.Parallel)
def split_data(data: Table, bucketing_func: Callable[[dict], StreamKey]) -> StreamsData:
    # TODO: Make this a unique column name
    index_col = "bucket_index"
    data.add_column(index_col, bucketing_func)
    data.materialize()
    # TODO: Make this not the least efficient thing I've ever seen
    results = {}
    for i in set(data[index_col]):  # type: ignore
        results[i] = data.select_rows(lambda r: r[index_col] == i).remove_column(
            index_col
        )
        results[i].materialize()
    return results


@define_pipe("copy_data_into_streams", result_type=PipeResult.Parallel)
def copy_data_into_streams(data: Table, *streams: StreamKey) -> StreamsData:
    streams_data = {}
    for i in streams:
        streams_data[i] = Table(data.to_petl())
    return streams_data


@define_pipe(
    "all_streams", input_type=PipeResult.Parallel, result_type=PipeResult.Parallel
)
def all_streams(data: StreamsData, inner_pipe: PipeBuilder) -> StreamsData:
    if (
        inner_pipe.input_type != PipeResult.Serial
        or inner_pipe.input_type != PipeResult.Serial
    ):
        raise RuntimeError("Cannot run a non serial-to-serial pipe on all streams")

    for i in data.keys():
        data[i] = inner_pipe.func(data[i])

    return data


# TODO: Refactor the streams concept to return PipeBuilders that contain other
# PipeBuilders, instead of running control flow themselves. This will allow the
# control flow to be handled by the Pipeline object instead.
@define_pipe(
    "for_streams", input_type=PipeResult.Parallel, result_type=PipeResult.Parallel
)
def for_streams(
    data: StreamsData, inner_pipes: Dict[StreamKey, PipeBuilder]
) -> StreamsData:
    for i in data.keys():
        if i in inner_pipes.keys():
            inner_pipe = inner_pipes[i].first_pipe

            while inner_pipe is not None:
                if (
                    inner_pipe.input_type != PipeResult.Serial
                    or inner_pipe.input_type != PipeResult.Serial
                ):
                    raise RuntimeError(
                        "Cannot run a non serial-to-serial pipe on all streams"
                    )

                data[i] = inner_pipe.func(data[i])
                inner_pipe = inner_pipe.next_pipe

    return data


def main():
    for csv in [
        "after_1975.csv",
        "before_1980.csv",
        "after_1979.csv",
        "after_1980.csv",
        "after_1990.csv",
        "lotr_books.csv",
    ]:
        if os.path.exists(csv):
            os.remove(csv)

    dirpath = Path("logging")
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)

    # fmt: off
    clean_year = lambda: (
        filter_rows({
            "Year": lambda year: year is not None
        })
    )(
        convert(
            "Year",
            lambda year_str: int(year_str)
        )
    )

    load_after_1975 = Pipeline(
        "Load after 1975",
        load_from_csv("deniro.csv")
        (
            clean_year()
        )(
            filter_rows({
                "Year": lambda year: year > 1975
            })
        )(
            write_csv("after_1975.csv")
        )
    )
    split_on_1980 = Pipeline(
        "Split on 1980",
        load_from_csv("deniro.csv")
        (
            clean_year()
        )(
            split_data(lambda row: "gte_1980" if row["Year"] >= 1980 else "lt_1980")
        )(
            for_streams({
                "lt_1980": write_csv("before_1980.csv"),
                "gte_1980": write_csv("after_1979.csv")
            })
        )
    )

    save_lotr_books = Pipeline(
        "Save LOTR Books",
        load_lotr_books_from_api()
        (
            write_csv("lotr_books.csv")
        )
    )

    copy_into_streams_test = Pipeline(
        "Copy into streams test",
        load_from_csv("deniro.csv")
        (
            clean_year()
        )(
            copy_data_into_streams("0", "1")
        )(
            for_streams({
                "0": filter_rows({
                    "Year": lambda year: year > 1990
                })(
                    write_csv("after_1990.csv")
                ),
                "1": write_csv("all_years.csv")
            })
        )
    )

    dashboard = Dashboard(
        split_on_1980,
        # save_lotr_books,
        # load_after_1975,
        # copy_into_streams_test,
        # logger=Loggers(
        #     # CsvLogger(),
        #     # BreakpointLogger()
        # )
    )
    dashboard.run()
    # dashboard.generate_report("report.html")
    # fmt: on


if __name__ == "__main__":
    main()
