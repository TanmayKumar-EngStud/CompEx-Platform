# Integration Testing Directory

This directory contains all the integration tests for the project. Integration tests are designed to test the interactions between different components of the system, ensuring that they work together as expected.

Unit tests, on the other hand, are located in a `.testing` subdirectory within the folder of the component they are testing. For example, a test for a file in `core/utils/` would be located in `core/utils/.testing/`.

All tests should be written using the `pytest` framework. The tests should be named using the `test_` prefix, and the files should be named using the `test_` prefix as well.

To run all the tests (both unit and integration), you can use the following command from the root directory:

```bash
pytest
```
