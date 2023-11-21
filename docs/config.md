<a id="config"></a>

# config

<a id="config.Config"></a>

## Config Objects

```python
class Config()
```

<a id="config.Config.__init__"></a>

#### \_\_init\_\_

```python
def __init__(sid, nyu_id=None)
```

Initializes the instance based on subject identifier.

**Arguments**:

- `sid` _str_ - Identifies subject.
- `nyu_id` _str, optional_ - Subject identifier on NYU server.

<a id="config.Config.configure_paths"></a>

#### configure\_paths

```python
def configure_paths()
```

Configurable filepaths.

<a id="config.Config.configure_paths_nyu"></a>

#### configure\_paths\_nyu

```python
def configure_paths_nyu()
```

Configurable filepaths on NYU server.

<a id="config.Config.write_config"></a>

#### write\_config

```python
def write_config()
```

Write YAML file containing configured information for each subject.

<a id="config.Config.read_config"></a>

#### read\_config

```python
def read_config()
```

Read YAML file containing configured information for each subject.

