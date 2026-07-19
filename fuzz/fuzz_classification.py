import hypothesis.strategies as st
from hypothesis import given
import rustchain.node.classification as classification

@given(st.dictionaries(st.text(), st.text()))
def test_fuzz_classification(payload):
    try:
        classification.derive_verified_device(payload)
    except Exception as e:
        # Log the exception if needed
        print(f"Exception: {e}")
        assert False, f"Fuzzing failed with payload: {payload}"

if __name__ == "__main__":
    test_fuzz_classification()
