<a id="classes/config"></a>

# classes/config

<a id="classes/config.Config"></a>

## Config Objects

```python
class Config()
```

<a id="classes/config.Config.__init__"></a>

#### \_\_init\_\_

```python
def __init__(sid, nyu_id=None)
```

Initializes the instance based on subject identifier.

**Arguments**:

- `sid` _str_ - Identifies subject.
- `nyu_id` _str, optional_ - Subject identifier on NYU server.

<a id="classes/config.Config.configure_paths_old"></a>

#### configure\_paths\_old

```python
def configure_paths_old()
```

Configurable filepaths.

<a id="classes/config.Config.configure_paths_nyu"></a>

#### configure\_paths\_nyu

```python
def configure_paths_nyu()
```

Configurable filepaths on NYU server.

<a id="classes/config.Config.write_config_old"></a>

#### write\_config\_old

```python
def write_config_old()
```

Write YAML file containing configured information for each subject.

<a id="classes/config.Config.read_config_old"></a>

#### read\_config\_old

```python
def read_config_old()
```

Read YAML file containing configured information for each subject.

