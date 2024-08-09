# Chat-DOCS

## Project Overview

Chat-DOCS is a python webapp for QnA with documents using Llama-3 model.

## Repository Contents

- **aoo.py**: Python script that provides a graphical user interface (GUI) using Streamlit to demonstrate the chat-DOCs.
- **requirements.txt**: List of Python libraries required to run `app.py`.

## Getting Started

### Prerequisites

Ensure you have the following installed:
- Python 3.11.9
- pip

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Lokesh-DataScience/Chat-DOCs.git
    cd Chat-DOCs
    ```

2. Install the required Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Demo

To run the GUI demo of the Chat-DOCs:

```bash
streamlit run app.py
```
### Usage
- **The app.py scripts open a window displaying the interface of streamlit.**
- **The model will take input from user as query and gives related and relevant.**
- 
### Model Details
- **The LangChain is used for QnABot is saved in the app.py file.**
- **This model is build to get data from `Documents` as per user query.**

### Contributing
- **Contributions are welcome! Please feel free to submit a Pull Request.**

### Acknowledgements
- **Streamlit for providing the tools for GUI and user interaction.**
- **Langchain for the model training.**

