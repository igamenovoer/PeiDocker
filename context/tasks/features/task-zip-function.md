# Implementing the download as zip function

Before we go, learn the terminology: `context/design/terminology.md`

Currently clicking the download button will trigger error, like this:

```
(pei-docker) PS D:\code\PeiDocker> pei-docker-gui start
Starting PeiDocker Web GUI on port 8080...
Open http://localhost:8080 in your browser
NiceGUI ready to go on http://localhost:8080, http://10.10.14.48:8080, http://169.254.197.23:8080, http://169.254.246.34:8080, http://169.254.37.236:8080, http://169.254.50.228:8080, http://169.254.62.192:8080, http://172.22.64.1:8080, http://192.168.144.1:8080, http://192.168.245.1:8080, http://192.168.48.194:8080, http://192.168.56.1:8080, and http://198.18.0.1:8080
http://127.0.0.1:8080/download/peidocker-20250806-183413.zip not found
The current slot cannot be determined because the slot stack for this task is empty.
This may happen if you try to create UI from a background task.
To fix this, enter the target slot explicitly using `with container_element:`.
  + Exception Group Traceback (most recent call last):
  |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 77, in collapse_excgroups
  |     yield
  |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 183, in __call__
  |     async with anyio.create_task_group() as task_group:
  |                ~~~~~~~~~~~~~~~~~~~~~~~^^
  |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\anyio\_backends\_asyncio.py", line 772, in __aexit__
  |     raise BaseExceptionGroup(
  |         "unhandled errors in a TaskGroup", self._exceptions
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    |     await self.app(scope, receive, _send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |                                    ~~~~~~~~~~~~~~~~~~^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    |     self.gen.throw(value)
    |     ~~~~~~~~~~~~~~^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 23, in dispatch
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    |     raise app_exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |                                    ~~~~~~~~~~~~~~~~~~^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    |     self.gen.throw(value)
    |     ~~~~~~~~~~~~~~^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 13, in dispatch
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    |     raise app_exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 29, in __call__
    |     await responder(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 130, in __call__
    |     await super().__call__(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 46, in __call__
    |     await self.app(scope, receive, self.send_with_compression)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 716, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 736, in app
    |     await route.handle(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 290, in handle
    |     await self.app(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 78, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 75, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 302, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     ...<3 lines>...
    |     )
    |     ^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 213, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 537, in download
    |     return ui.download(str(zip_path), f'{project_name}.zip')
    |            ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 29, in __call__
    |     self.file(src, filename, media_type)
    |     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 46, in file
    |     context.client.download(src, filename, media_type)
    |     ^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 31, in client
    |     return self.slot.parent.client
    |            ^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 23, in slot
    |     raise RuntimeError('The current slot cannot be determined because the slot stack for this task is empty.\n'
    |                        'This may happen if you try to create UI from a background task.\n'
    |                        'To fix this, enter the target slot explicitly using `with container_element:`.')
    | RuntimeError: The current slot cannot be determined because the slot stack for this task is empty.
    | This may happen if you try to create UI from a background task.
    | To fix this, enter the target slot explicitly using `with container_element:`.
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    with recv_stream, send_stream, collapse_excgroups():
                                   ~~~~~~~~~~~~~~~~~~^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 23, in dispatch
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    raise app_exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    with recv_stream, send_stream, collapse_excgroups():
                                   ~~~~~~~~~~~~~~~~~~^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 13, in dispatch
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    raise app_exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 29, in __call__
    await responder(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 130, in __call__
    await super().__call__(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 46, in __call__
    await self.app(scope, receive, self.send_with_compression)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 78, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 75, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 302, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 213, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 537, in download
    return ui.download(str(zip_path), f'{project_name}.zip')
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 29, in __call__
    self.file(src, filename, media_type)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 46, in file
    context.client.download(src, filename, media_type)
    ^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 31, in client
    return self.slot.parent.client
           ^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 23, in slot
    raise RuntimeError('The current slot cannot be determined because the slot stack for this task is empty.\n'
                       'This may happen if you try to create UI from a background task.\n'
                       'To fix this, enter the target slot explicitly using `with container_element:`.')
RuntimeError: The current slot cannot be determined because the slot stack for this task is empty.
This may happen if you try to create UI from a background task.
To fix this, enter the target slot explicitly using `with container_element:`.
ERROR:    Exception in ASGI application
  + Exception Group Traceback (most recent call last):
  |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 77, in collapse_excgroups
  |     yield
  |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 183, in __call__
  |     async with anyio.create_task_group() as task_group:
  |                ~~~~~~~~~~~~~~~~~~~~~~~^^
  |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\anyio\_backends\_asyncio.py", line 772, in __aexit__
  |     raise BaseExceptionGroup(
  |         "unhandled errors in a TaskGroup", self._exceptions
  |     ) from None
  | ExceptionGroup: unhandled errors in a TaskGroup (1 sub-exception)
  +-+---------------- 1 ----------------
    | Traceback (most recent call last):
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 409, in run_asgi
    |     result = await app(  # type: ignore[func-returns-value]
    |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |         self.scope, self.receive, self.send
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     )
    |     ^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
    |     return await self.app(scope, receive, send)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\applications.py", line 1054, in __call__
    |     await super().__call__(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\applications.py", line 113, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    |     await self.app(scope, receive, _send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |                                    ~~~~~~~~~~~~~~~~~~^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    |     self.gen.throw(value)
    |     ~~~~~~~~~~~~~~^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 23, in dispatch
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    |     raise app_exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    |     with recv_stream, send_stream, collapse_excgroups():
    |                                    ~~~~~~~~~~~~~~~~~~^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    |     self.gen.throw(value)
    |     ~~~~~~~~~~~~~~^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    |     response = await self.dispatch_func(request, call_next)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 13, in dispatch
    |     response = await call_next(request)
    |                ^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    |     raise app_exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    |     await self.app(scope, receive_or_disconnect, send_no_error)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 29, in __call__
    |     await responder(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 130, in __call__
    |     await super().__call__(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 46, in __call__
    |     await self.app(scope, receive, self.send_with_compression)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    |     await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 716, in __call__
    |     await self.middleware_stack(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 736, in app
    |     await route.handle(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 290, in handle
    |     await self.app(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 78, in app
    |     await wrap_app_handling_exceptions(app, request)(scope, receive, send)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    |     raise exc
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    |     await app(scope, receive, sender)
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 75, in app
    |     response = await f(request)
    |                ^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 302, in app
    |     raw_response = await run_endpoint_function(
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |     ...<3 lines>...
    |     )
    |     ^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 213, in run_endpoint_function
    |     return await dependant.call(**values)
    |            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 537, in download
    |     return ui.download(str(zip_path), f'{project_name}.zip')
    |            ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 29, in __call__
    |     self.file(src, filename, media_type)
    |     ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 46, in file
    |     context.client.download(src, filename, media_type)
    |     ^^^^^^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 31, in client
    |     return self.slot.parent.client
    |            ^^^^^^^^^
    |   File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 23, in slot
    |     raise RuntimeError('The current slot cannot be determined because the slot stack for this task is empty.\n'
    |                        'This may happen if you try to create UI from a background task.\n'
    |                        'To fix this, enter the target slot explicitly using `with container_element:`.')
    | RuntimeError: The current slot cannot be determined because the slot stack for this task is empty.
    | This may happen if you try to create UI from a background task.
    | To fix this, enter the target slot explicitly using `with container_element:`.
    +------------------------------------

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 409, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\applications.py", line 1054, in __call__
    await super().__call__(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\applications.py", line 113, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    with recv_stream, send_stream, collapse_excgroups():
                                   ~~~~~~~~~~~~~~~~~~^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 23, in dispatch
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    raise app_exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 182, in __call__
    with recv_stream, send_stream, collapse_excgroups():
                                   ~~~~~~~~~~~~~~~~~~^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\contextlib.py", line 162, in __exit__
    self.gen.throw(value)
    ~~~~~~~~~~~~~~^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_utils.py", line 83, in collapse_excgroups
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 184, in __call__
    response = await self.dispatch_func(request, call_next)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\middlewares.py", line 13, in dispatch
    response = await call_next(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 159, in call_next
    raise app_exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\base.py", line 144, in coro
    await self.app(scope, receive_or_disconnect, send_no_error)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 29, in __call__
    await responder(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 130, in __call__
    await super().__call__(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\gzip.py", line 46, in __call__
    await self.app(scope, receive, self.send_with_compression)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 78, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\starlette\routing.py", line 75, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 302, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\fastapi\routing.py", line 213, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\src\pei_docker\webgui\app.py", line 537, in download
    return ui.download(str(zip_path), f'{project_name}.zip')
           ~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 29, in __call__
    self.file(src, filename, media_type)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\functions\download.py", line 46, in file
    context.client.download(src, filename, media_type)
    ^^^^^^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 31, in client
    return self.slot.parent.client
           ^^^^^^^^^
  File "D:\code\PeiDocker\.pixi\envs\default\Lib\site-packages\nicegui\context.py", line 23, in slot
    raise RuntimeError('The current slot cannot be determined because the slot stack for this task is empty.\n'
                       'This may happen if you try to create UI from a background task.\n'
                       'To fix this, enter the target slot explicitly using `with container_element:`.')
RuntimeError: The current slot cannot be determined because the slot stack for this task is empty.
This may happen if you try to create UI from a background task.
To fix this, enter the target slot explicitly using `with container_element:`.
```

Fix this and implement the download functionality correctly

- when `download` is clicked, it should create a zip file of the project directory and triggers the download of that zip file
- for reference, see `context\hints\nicegui-kb\howto-nicegui-zip-directory-download.md`