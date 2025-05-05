import os
import sys
import pytest
from unittest.mock import MagicMock
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from renderer import Renderer

def test_update_uniforms_sets_matrices():
    renderer = Renderer()
    renderer.program = MagicMock()
    m = v = p = np.zeros(16, dtype=np.float32)
    renderer.update_uniforms(m, v, p)
    renderer.program.__setitem__.assert_any_call('modelMatrix', m)
    renderer.program.__setitem__.assert_any_call('viewMatrix', v)
    renderer.program.__setitem__.assert_any_call('projectionMatrix', p)
