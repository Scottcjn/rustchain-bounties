"""Collection-time shims for the legacy ML stack present in CI.

The repository's tests do not need TensorFlow, but the image ships an old
TensorFlow/Gym combination whose import path touches ``tf.contrib`` -- an
attribute that was removed in TensorFlow 2.x.  That raises during pytest
collection and aborts the whole run before any test can execute.

Keep this file tiny and defensive: it only fills in the missing attribute
(or does nothing at all when TensorFlow is absent), so import behaviour for
the rest of the project is unchanged.
"""

import os
import sys
import types

# Ask optional libraries not to pull TensorFlow in at all.
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")


class _StubModule(types.ModuleType):
    """Module whose attributes are lazily created stub submodules."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        child = _StubModule("{}.{}".format(self.__name__, name))
        child.__path__ = []
        setattr(self, name, child)
        return child


def _patch_tensorflow_contrib():
    """Restore a harmless ``tensorflow.contrib`` placeholder if missing."""
    try:
        import tensorflow as tf
    except Exception:
        return

    if hasattr(tf, "contrib"):
        return

    contrib = _StubModule("tensorflow.contrib")
    contrib.__path__ = []
    try:
        tf.contrib = contrib
    except Exception:
        return

    sys.modules.setdefault("tensorflow.contrib", contrib)


try:
    _patch_tensorflow_contrib()
except Exception:
    # Environment patching must never break test collection.
    pass
