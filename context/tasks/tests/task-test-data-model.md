now we need to test if the `ui-data-model` can be correctly transformed to the `peidocker-data-model` and vice versa, no need to care about GUI yet, just test the data model.

Terminology: see `context\tasks\prefix\prefix-terminology.md` for the terminology used in this task, especially the `peidocker-data-model` and `ui-data-model`.

You can use `context\tasks\tests\test-case-2.md` as a test case, just create `ui-data-model` objects, fill the contents, and then use the `ui-data-adapter` to convert it to `peidocker-data-model`, and then 