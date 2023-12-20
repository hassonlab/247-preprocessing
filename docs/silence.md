<a id="classes/silence"></a>

# classes/silence

<a id="classes/silence.Silence"></a>

## Silence Objects

```python
@traced

@logged
class Silence()
```

File containing marked silences corresponding to a specific audio file.

...

**Attributes**:

- `file` _PosixPath_ - Path to the silence file.

<a id="classes/silence.Silence.__init__"></a>

#### \_\_init\_\_

```python
def __init__(file)
```

Initializes the instance based on file identifier.

**Arguments**:

- `file` _PosixPath_ - Path to file.

<a id="classes/silence.Silence.read_silence"></a>

#### read\_silence

```python
def read_silence()
```

Read silence file to Pandas DataFrame

<a id="classes/silence.Silence.calc_silence"></a>

#### calc\_silence

```python
def calc_silence()
```

Convert times in table to timedelta

