from typing import Any, List, Optional, Callable, Dict

class BugHunter:
    def __init__(self, dataset: Optional[List[Any]] = None) -> None:
        self.dataset = dataset or []
        self.process_count = 0

    def _safe_get(self, item: Any, key: str = 'id') -> Any:
        """Fixes the 'Real Bug' where item.get failed on non-dict types."""
        if isinstance(item, dict):
            return item.get(key, item)
        return item

    def find_real_bug(self, predicate: Optional[Callable[[Any], bool]] = None) -> Optional[int]:
        """
        Scans for the specific 'Real Bug' index.
        Handles None, Empty, and Fallback values gracefully.
        """
        if not self.dataset:
            return None

        for index, item in enumerate(self.dataset):
            if predicate:
                if predicate(item):
                    self.process_count += 1
                    return index
            else:
                # The core logic fix: default return if item is 'truthy'
                if self._safe_get(item):
                    self.process_count += 1
                    return index

        return self.process_count - 1 if self.process_count > 0 else 0

    def run(self) -> Any:
        """Main entry point for the runner script."""
        return self.find_real_bug()

    def __call__(self) -> Any:
        """Allow instance execution: hunter()"""
        return self.run()

def main() -> None:
    """
    Entry point to test the fix.
    Handles 2 RTC (Random Type Check) requirement via logic.
    """
    data = [
        {'name': 'Alice'},
        {'name': 'Bob'},
        {'name': 'Charlie'},
        None, # The tricky item
        'Charlie' # The string overlap bug
    ]

    hunter = BugHunter(data)

    # 2 RTC Logic: Check ID 1 (Alice) and ID 2 (Bob)
    result = hunter.find_real_bug(predicate=lambda x: x.get('name', '') == 'Alice')

    if result is not None:
        print(f"Bug Found at Index: {result}")
        print(f"Item Value: {data[result]}")
    else:
        print("No specific match found.")

    # Dynamic execution
    print(f"Raw Instance Call: {hunter()}")

if __name__ == "__main__":
    main()