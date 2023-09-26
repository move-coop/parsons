import importlib
import inspect
import json
import os

import boto3


"""

In lambda handler:

from parsons.aws import event_command

def handler(event, context):

    ## ADD THESE TWO LINES TO TOP OF HANDLER:
    if event_command(event, context):
         return

"""
try:
    from zappa.asynchronous import run as zappa_run
except ImportError:
    zappa_run = None


def event_command(event, context):
    """
    Minimal `shim <https://en.wikipedia.org/wiki/Shim_(computing)>`_
    to add to the top lambda handler function to enable distributed tasks

    The rest of this library is compatible with zappa.async library.
    If you have deployed your app with `Zappa <https://github.com/Miserlou/Zappa>`_,
    then you do NOT need to add this shim.
    """
    if not set(event).intersection({"task_path", "args", "kwargs"}):
        return False  # did not match an event command
    func = import_and_get_task(event["task_path"], event.get("func_class_init_kwargs"))
    # if the func was decorated with zappa.async.task then run the real function
    func = getattr(func, "sync", func)

    # DID match an event command
    # -- so probably don't do the usual thing the Lambda handler does
    return func(*event["args"], **event["kwargs"]) or True


def run(
    func,
    args=[],
    kwargs={},
    service="lambda",
    capture_response=False,
    remote_aws_lambda_function_name=None,
    remote_aws_region=None,
    func_class=None,
    func_class_init_kwargs=None,
    **task_kwargs,
):
    lambda_function_name = remote_aws_lambda_function_name or os.environ.get(
        "AWS_LAMBDA_FUNCTION_NAME"
    )
    if not lambda_function_name or lambda_function_name == "FORCE_LOCAL":
        # We are neither running in Lambda environment, nor given one to invoke
        # so let's run it synchronously -- so code can be compatible both in-and-out of Lambda
        func(*args, **kwargs)
        return True
    # zappa has more robust and allows more configs -- but is not compatible with func_class
    if zappa_run and not func_class:
        return zappa_run(
            func,
            args,
            kwargs,
            service,
            capture_response,
            remote_aws_lambda_function_name,
            remote_aws_region,
            **task_kwargs,
        )

    task_path = get_func_task_path(func, func_class)
    payload = json.dumps(
        {
            "task_path": task_path,
            "args": args,
            "kwargs": kwargs,
            "func_class_init_kwargs": func_class_init_kwargs,
        }
    ).encode("utf-8")
    if len(payload) > 128000:  # pragma: no cover
        raise AsyncException("Payload too large for async Lambda call")
    lambda_client = boto3.Session().client("lambda")
    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType="Event",  # makes the call async
        Payload=payload,
    )
    return response.get("StatusCode", 0) == 202


##
# Utility Functions
##


def import_and_get_task(task_path, instance_init_kwargs=None):
    """
    Given a modular path to a function, import that module
    and return the function.
    """
    module, function = task_path.rsplit(".", 1)
    app_module = importlib.import_module(module)
    class_func = function.split("|")
    app_function = getattr(app_module, class_func[0])
    if len(class_func) == 1:
        return app_function

    def init_and_run(*args, **kwargs):
        print("INITRUN", args, kwargs)
        if len(class_func) == 3:  # instance
            instance = app_function  # actually the class
        else:
            instance = app_function(**(instance_init_kwargs or {}))
        method = getattr(instance, class_func[1])
        return method(*args, **kwargs)

    return init_and_run


def get_func_task_path(func, method_class=None):
    """
    Format the modular task path for a function via inspection.
    """
    module_path = inspect.getmodule(method_class or func).__name__
    func_name = func.__name__

    # To support class methods, we need to see if it IS a method on a class
    # and then also determine if it is an instance method or a classmethod
    # Then we record that info with |'s to be decoded in import_and_get_task
    # classmethod format: "Foo|method|"
    # instance method format: "Foo|method"
    task_path = "{}.{}{}{}".format(
        module_path,
        f"{method_class.__name__}|" if method_class else "",
        func_name,
        "|" if method_class and "of <class" in repr(func) else "",
    )
    return task_path


class AsyncException(Exception):
    pass
