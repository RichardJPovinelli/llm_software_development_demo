<!--
MIT License

Copyright (c) 2026 Richard J Povinelli

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
-->

# Python Style Guide With Functional Preferences

This guide establishes coding preferences for this repository. It favors a functional style where practical, especially for data transformations, feature construction, validation logic, and other business logic that benefits from predictable behavior and focused tests.

At the same time, this repository includes training loops, serialization, wrapper integration, data loading, plotting, and other tasks that necessarily involve side effects or controlled mutable state. In those areas, the goal is not strict purity for its own sake, but code that is clear, well-bounded, and easy to validate.

## Preferred Design Principles

### 1. Prefer Pure Functions For Data Logic

Prefer pure functions for transformations, feature construction, channel normalization, aggregation rules, metrics, and other data logic. Given the same inputs, these helpers should return the same outputs without hidden dependencies or side effects whenever practical.

**Good:**

```python
def standardize_channel_names(
    raw_names: list[str],
    rename_map: dict[str, str],
) -> list[str]:
    """Return normalized channel names without mutating the input."""
    return [rename_map.get(name.lower(), name.lower()) for name in raw_names]


def aggregate_window_probabilities(probabilities: list[float]) -> float:
    """Map window-level probabilities to a record-level score."""
    if not probabilities:
        raise ValueError("probabilities must not be empty")
    return sum(probabilities) / len(probabilities)
```

**Avoid:**

```python
# Bad: depends on hidden global state
CHANNEL_RENAME_MAP = {}


def standardize_channel_names(raw_names: list[str]) -> list[str]:
    return [CHANNEL_RENAME_MAP.get(name.lower(), name.lower()) for name in raw_names]


# Bad: mutates a caller-owned list in place
def clip_probabilities(probabilities: list[float]) -> list[float]:
    for i, value in enumerate(probabilities):
        probabilities[i] = min(max(value, 0.0), 1.0)
    return probabilities
```

### 2. Prefer Immutable Interfaces

Prefer helper interfaces that avoid mutating caller-owned inputs. Return new values when feasible, and use tuples, frozen dataclasses, or other stable structures for configuration and metadata that should not drift during execution.

**Good:**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class WindowConfig:
    sample_rate_hz: int
    window_seconds: int
    channel_order: tuple[str, ...]


def with_required_channels(
    observed_channels: tuple[str, ...],
    required_channels: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(channel for channel in required_channels if channel in observed_channels)
```

**Avoid:**

```python
# Bad: mutable config shared across the pipeline
WINDOW_CONFIG = {
    "sample_rate_hz": 200,
    "window_seconds": 30,
    "channel_order": ["f3", "f4", "c3", "c4"],
}


def configure_for_debug_mode() -> dict:
    WINDOW_CONFIG["window_seconds"] = 5
    return WINDOW_CONFIG
```

Mutable arrays, tensors, and model objects are still allowed when required by libraries or performance constraints. The main goal is to avoid surprising mutation at module boundaries and to keep mutable state localized.

### 3. Functional Core, Imperative Shell

Keep the core logic of a pipeline as pure and composable as practical, and isolate file I/O, EDF loading, model execution, checkpointing, CLI handling, and other side effects in thin orchestration layers.

**Good:**

```python
def build_dummy_channel_mask(
    observed_channels: set[str],
    expected_channels: tuple[str, ...],
) -> list[int]:
    """Pure helper used by both training and inference."""
    return [0 if channel in observed_channels else 1 for channel in expected_channels]


def load_record_inputs(record_path: str, expected_channels: tuple[str, ...]) -> dict:
    """Thin I/O wrapper around pure helpers."""
    raw_signals = read_record(record_path)
    observed_channels = set(raw_signals)
    dummy_mask = build_dummy_channel_mask(observed_channels, expected_channels)
    return {"signals": raw_signals, "dummy_mask": dummy_mask}
```

**Avoid:**

```python
# Bad: mixes disk access, mutation, and transformation in one place
def build_training_examples(record_path: str) -> dict:
    signals = read_record(record_path)
    if "c3" not in signals:
        signals["c3"] = signals["f3"]  # hidden fallback policy
    signals["f3"] = normalize_signal(signals["f3"])
    write_debug_snapshot(record_path, signals)
    return signals
```

### 4. Isolate Stateful Framework Code

Scientific Python and machine learning libraries often require mutable arrays, tensors, model objects, optimizers, and serialization payloads. Keep that state in small, well-named orchestration functions or classes, and avoid spreading framework-specific mutation through core data logic.

**Good:**

```python
import numpy as np

def normalize_window(window: np.ndarray) -> np.ndarray:
    """Pure helper that returns a new normalized array."""
    scale = np.max(np.abs(window))
    if scale == 0:
        return window.copy()
    return window / scale


def run_training_step(model, optimizer, batch: dict) -> float:
    """Keep framework mutation localized to the training shell."""
    optimizer.zero_grad()
    logits = model(batch["inputs"])
    loss = compute_loss(logits, batch["labels"])
    loss.backward()
    optimizer.step()
    return float(loss.item())
```

**Avoid:**

```python
# Bad: framework state leaks into unrelated data logic
MODEL_STATE = {}


def score_windows(windows):
    MODEL_STATE["last_batch_size"] = len(windows)
    MODEL_STATE["predictions"] = model(windows)
    return postprocess_predictions(MODEL_STATE["predictions"])
```

### 5. Small, Single-Purpose Functions

Prefer functions that do one job at one level of abstraction. Small helpers are easier to test, reuse, and combine into predictable pipelines.

**Good:**

```python
def discover_record_paths(data_root: str) -> list[str]:
    """Discover candidate record paths."""
    pass


def standardize_record_channels(raw_signals: dict[str, object]) -> dict[str, object]:
    """Normalize channel names and drop unsupported labels."""
    pass


def build_record_windows(signals: dict[str, object], window_seconds: int) -> list[object]:
    """Split a record into fixed-length windows."""
    pass


def prepare_record_examples(record_path: str, window_seconds: int) -> list[object]:
    raw_signals = read_record(record_path)
    standardized = standardize_record_channels(raw_signals)
    return build_record_windows(standardized, window_seconds)
```

**Avoid:**

```python
# Bad: one function discovers records, loads data, mutates state,
# computes features, logs errors, and writes outputs
def process_dataset(data_root: str) -> dict:
    ...
```

### 6. Prefer Simple, Explicit Data Pipelines

Build pipelines from small, readable steps. Prefer comprehensions, focused helpers, and explicit transformation stages over clever abstractions. Use `map` and `filter` when they improve readability, not as a default.

**Good:**

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingConfig:
    window_seconds: int


def build_training_examples(record_paths: list[str], config: TrainingConfig) -> list[dict]:
    return [
        attach_window_labels(
            build_record_windows(
                standardize_record_channels(read_record(path)),
                config.window_seconds,
            ),
            load_record_label(path),
        )
        for path in record_paths
    ]
```

**Avoid:**

```python
# Bad: opaque pipeline with hidden side effects and unclear stages
def build_training_examples(record_paths):
    return compose(audit_examples, cache_examples, shuffle_examples, load_examples)(record_paths)
```

### 7. Type Hints

Use type hints to make function boundaries, data contracts, and serialization expectations easier to understand. Prioritize type hints on public helpers, pipeline stages, config objects, and data exchanged between training and inference code.

**Good:**

```python
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class AggregationConfig:
    method: str


def aggregate_window_probabilities(
    probabilities: Sequence[float],
    config: AggregationConfig,
) -> float:
    if config.method != "mean":
        raise ValueError(f"Unsupported aggregation method: {config.method}")
    return sum(probabilities) / len(probabilities)
```

**Avoid:**

```python
# Bad: unclear boundary between inputs, config, and outputs
def aggregate_window_probabilities(probabilities, config):
    ...
```

## Stateful ML Components

Mutable training and inference state is allowed when it is required by the framework or by performance considerations. Model parameters, optimizer state, schedulers, checkpoint payloads, and training-history trackers may all be stateful.

- Keep stateful ML code localized to training and inference orchestration.
- Avoid mixing checkpoint management, logging, and metrics computation into low-level data transforms.
- Prefer passing plain tensors, arrays, and typed configs into helpers rather than reaching into global model state.
- Keep serialization boundaries explicit so saved artifacts can be understood and validated independently.

## Testing Guidance

Align test scope with code scope.

- Test pure helpers with focused unit tests and small concrete inputs.
- Use fixture-based tests for channel normalization, dummy-channel generation, window construction, aggregation rules, metrics, and other deterministic data logic.
- Add smoke or integration tests for orchestration code such as training entry points, inference paths, and wrapper-facing interfaces.
- Add serialization round-trip tests for artifacts that must survive from training to inference.
- Prefer simple examples over heavy mocking when validating pure transformations.

**Good:**

```python
def test_aggregate_window_probabilities_mean():
    result = aggregate_window_probabilities([0.2, 0.6, 0.4], AggregationConfig(method="mean"))
    assert result == 0.4


def test_build_dummy_channel_mask_marks_missing_channels():
    observed = {"f3", "c3"}
    expected = ("f3", "f4", "c3")
    assert build_dummy_channel_mask(observed, expected) == [0, 1, 0]
```

## When to Break These Rules

These preferences are meant to improve clarity, reliability, and testability. They are not absolute.

1. **Framework constraints**: training loops, model objects, tensors, and optimizer state may require controlled mutability.
2. **Performance-critical paths**: in-place operations or tighter coupling may be acceptable when they are materially simpler or faster.
3. **Wrapper compatibility**: submission-facing contracts may require less-than-ideal structure to preserve compatibility.
4. **Legacy integrations**: older code or third-party APIs may require adapter layers rather than fully pure interfaces.

When departing from the preferred functional style, make the reason clear through structure, naming, docstrings, or a brief comment when helpful.

## References

- [Functional Programming in Python](https://docs.python.org/3/howto/functional.html)
- [PEP 20 – The Zen of Python](https://www.python.org/dev/peps/pep-0020/)

## Decision Rule

- If code mainly transforms data, prefer a pure function.
- If code touches files, models, devices, randomness, or process state, isolate that side effect.
- If strict functional style makes the code harder to understand or validate, prefer clarity and testability over purity.
