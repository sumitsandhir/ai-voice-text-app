# Voice Recognition AI

A voice recognition AI application that listens to users, identifies whether the speaker is the owner or another user, and provides appropriate responses. When a different user (not the owner) activates the application, the responses are highlighted.

# Download ollama from website 
 
 https://ollama.com/


## Features

- **Voice Recognition**: Converts speech to text using Web Speech API or local models
- **User Identification**: Identifies whether the speaker is the owner or another user
- **Response Generation**: Generates appropriate responses to user queries
- **Visual Highlighting**: Highlights responses when a different user is detected

---

### 2. **Navigate to project directory**
### 3. **Remove any existing virtual environment**
rm -rf .venv
### 4. **Create a new virtual environment with Homebrew Python**

- On Apple Silicon (M1/M2/M3):

    ```
    /opt/homebrew/bin/python3 -m venv .venv
    ```

- On Intel Macs:

    ```
    /usr/local/bin/python3 -m venv .venv
    ```

*(If unsure, run `which python3` after Homebrew install to confirm the correct path.)*

### 5. **Activate the virtual environment**
 source .venv/bin/activate

### 6. **Upgrade pip (recommended)**
 pip install --upgrade pip

### 7. **Install all Python dependencies**
 pip install -r requirements.txt

``` 
---

## Additional Python Steps

### **Install OpenAI Whisper (for local transcription)**
```
 pip install git+[https://github.com/openai/whisper.git](https://github.com/openai/whisper.git)

``` 
---

## PySimpleGUI Troubleshooting

If you encounter:AttributeError: module 'PySimpleGUI' has no attribute 'theme'

```
#### **Do This:**

1. **Ensure no file named `PySimpleGUI.py` in your project directory**  
   This can shadow the installed package.

2. **Uninstall any problematic install and reinstall a proper version:**
    ```
    pip uninstall PySimpleGUI -y
    pip install "PySimpleGUI>=4.60.5"
    ```
   Update your `requirements.txt` as:
    ```
    PySimpleGUI>=4.60.5
    ```

3. **Check installation:**
    ```python
    import PySimpleGUI as sg
    sg.theme('DarkBlue')
    ```

---

## Tkinter Troubleshooting

To ensure that you are using modern Tcl/Tk (recommended for macOS):
sh python3 -c "import tkinter; print(tkinter.TkVersion)"


## Requirements

- Python 3.9+
- [Homebrew Python](https://docs.brew.sh/Homebrew-and-Python) recommended on macOS for latest Tcl/Tk support (for GUI)
- Modern web browser that supports Web Speech API (for web app)
- Microphone for audio input
- Internet connection (for some features)

---

#You should see `8.6` or higher. If you see `8.5`, recreate your `.venv` using the Homebrew Python as shown above.

---

### Python Application

- Run the Python app as needed, e.g.:
    ```sh
    python run_simple_ui.py
    ```
- Follow on-screen instructions for recording, registering voice, and interacting.

---

## How It Works

### Voice Recognition
The application uses the Web Speech API (for web) or OpenAI Whisper (for local Python) to capture audio from the microphone and convert it to text.

### Response Generation
Responses are generated based on the input question, often including both text and code examples where relevant.

---

## Customization

You can customize the application by:

1. Adding more response categories in the response generation logic
2. Adjusting the similarity threshold for user identification
3. Modifying the UI components and styling

---

## Limitations

- User identification is based on voice characteristics and is not 100% accurate
- Speech recognition may require an internet connection
- Response generation is rule-based and limited to predefined categories (by default)
- Browser compatibility for the Web Speech API may vary

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
