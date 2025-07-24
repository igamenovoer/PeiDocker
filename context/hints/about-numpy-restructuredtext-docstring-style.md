# About NumPy reStructuredText Documentation Style

This guide covers the NumPy documentation style using reStructuredText (reST) format with the `numpydoc` extension.

## Key Principles

- NumPy uses the **numpydoc** Sphinx extension to parse and render docstrings
- Follows reStructuredText (reST) syntax with NumPy-specific section conventions
- Sections like `Parameters`, `Returns`, `Notes` are converted to field lists
- Examples should NOT require `import numpy as np` in docstrings

## Basic Docstring Structure

```python
def example_function(param1, param2):
    """Brief one-line description.

    Optional longer description with more details about the function's
    behavior and usage.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str, optional
        Description of param2. Default is None.

    Returns
    -------
    bool
        True if successful, False otherwise.

    Raises
    ------
    ValueError
        If param1 is negative.

    Notes
    -----
    Additional notes about implementation or mathematical details.

    Examples
    --------
    >>> example_function(5, "test")
    True
    """
    pass
```

## Section Guidelines

### Parameters Section
```python
Parameters
----------
x : array_like
    Input array.
axis : int, optional
    Axis along which to operate. Default is None.
out : ndarray, optional
    Alternative output array. Must have same shape as expected output.
```

### Returns Section
```python
Returns
-------
result : ndarray
    Output array with same shape as input.
```

### Multiple Returns
```python
Returns
-------
mean : ndarray
    The arithmetic mean along the specified axis.
std : ndarray
    The standard deviation along the specified axis.
```

## Common reST Markup in NumPy

### Code References
- Use double backticks for code: `` `numpy.array` ``
- Function references: `` `func` `` or `` `module.func` ``
- Parameter references: `` `param_name` ``

### Math Expressions
```rst
.. math::
    
    \sum_{i=0}^{n} x_i^2
```

### Notes and Warnings
```rst
.. note::
    This is an important note.

.. warning::
    This is a warning about potential issues.
```

### Code Blocks
```rst
.. code-block:: python

    import numpy as np
    arr = np.array([1, 2, 3])
```

## Examples Section Best Practices

- Use `>>>` for interactive examples
- Don't import NumPy in examples (assumed to be available)
- Show expected output
- Keep examples concise and focused

```python
Examples
--------
>>> a = array([1, 2, 3])
>>> np.sum(a)
6
>>> np.sum(a, axis=0)
6
```

## Common Sections in NumPy Docstrings

| Section | Purpose |
|---------|---------|
| `Parameters` | Function/method parameters |
| `Returns` | Return values |
| `Yields` | For generator functions |
| `Raises` | Exceptions that may be raised |
| `See Also` | Related functions |
| `Notes` | Implementation details |
| `References` | Academic references |
| `Examples` | Usage examples |

## Source Links
- [NumPy Documentation Guide](https://numpy.org/doc/stable/dev/howto-docs.html)
- [Numpydoc Style Guide](https://numpydoc.readthedocs.io/en/latest/format.html)
- [NumPy GitHub Documentation](https://github.com/numpy/numpy/tree/main/doc)
