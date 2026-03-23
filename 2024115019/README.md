# README

## How to run the code

1. Navigate to the relevant directory (whitebox, integration, or blackbox).
2. Follow the instructions in each report.pdf for running code/tests for that section.
3. For Python code, use:
   ```sh
   python <script>.py
   ```
   or for tests:
   ```sh
   pytest
   ```

## How to run the tests

- For whitebox and integration tests:
  ```sh
  cd <rollnumber>/whitebox/tests
  pytest
  ```
  or
  ```sh
  cd <rollnumber>/integration/tests
  pytest
  ```
- For blackbox API tests:
  ```sh
  cd <rollnumber>/blackbox/tests
  pytest
  ```

## GitHub Repository

[Link to your GitHub repository](https://github.com/vai1717/dass-assignment-2)

---
## One Drive link


## Repository Structure

```text
.
|____README.md
|____blackbox
| |____blackbox.pdf
| |____tests
| | |____test_quickcart_api.py
| | |____test_results.txt
|____integration
| |____code
| | |______init__.py
| | |____call_graph.dot
| | |____crew_management.py
| | |____garage.py
| | |____inventory.py
| | |____main.py
| | |____mission_planning.py
| | |____race_management.py
| | |____registration.py
| | |____results.py
| | |____sponsorship.py
| | |____tests
| | | |______init__.py
| |____diagrams
| | |____call_graph.jpg
| |____integration.pdf
| |____tests
| | |______init__.py
| | |____test_integration.py
|____whitebox
| |____code
| | |____moneypoly
| | | |____README.md
| | | |____main.py
| | | |____moneypoly
| | | | |____bank.py
| | | | |____board.py
| | | | |____cards.py
| | | | |____config.py
| | | | |____dice.py
| | | | |____game.py
| | | | |____player.py
| | | | |____property.py
| | | | |____ui.py
| |____diagrams
| | |____CFG.jpg
| |____tests
| | |____test_whitebox.py
| |____whitebox.pdf
```
