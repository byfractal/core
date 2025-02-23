## Prerequisites
- Python : latest version
- Required libraries (see `requirements.txt`)
- Remove any existing files in the `data/raw/`, `data/processed/`, and `data/filtered/` directories to test the application.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/byfractal/core.git
   cd core
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Configure your `.env` file with the necessary variables.
2. Run the application:
   ```bash
   python app/api.py
   ```

## Contributing
Steps:
1. Fork the project.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.
