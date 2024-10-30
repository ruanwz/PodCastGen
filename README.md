# PodCastGen

PodCastGen is a Python application that generates podcast scripts and corresponding audio using AI technologies. It leverages PocketGroq for script generation and Edge-TTS for text-to-speech conversion, supporting multiple languages and voice options.

![PodCastGen Demo](https://asciinema.org/a/7ff3nkO4P8GnwoCoy01gECMOk)



## Table of Contents
1. [Installation](#installation)
2. [Usage](#usage)
3. [Configuration](#configuration)
4. [Voice Configuration](#voice-configuration)
5. [Operational Parameters](#operational-parameters)
6. [Dependencies](#dependencies)
7. [Additional Resources](#additional-resources)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/podcastgen.git
   cd podcastgen
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your GROQ API key as an environment variable:
   ```
   export GROQ_API_KEY=your_api_key_here
   ```
   On Windows, use `set GROQ_API_KEY=your_api_key_here`

## Usage

PodCastGen supports multiple input sources and voice options:

1. Generate a new script and audio:
   ```
   python podcastgen.py <input_source> <output_directory>
   ```

2. Use a pre-written script:
   ```
   python podcastgen.py <input_source> <output_directory> --use-script
   ```

3. List available voices:
   ```
   python podcastgen.py --list-voices
   ```

4. List voices for specific language:
   ```
   python podcastgen.py --list-language zh-CN
   ```

5. Specify custom voices:
   ```
   python podcastgen.py <input_source> <output_directory> --male-voice "zh-CN-YunxiNeural" --female-voice "zh-CN-XiaoxiaoNeural"
   ```

Input sources can be:
- Local text files (.txt)
- YouTube URLs (will extract transcripts)
- Web URLs (will extract main content)

## Configuration

Create a `config.py` file in the project directory with the following content:

```python
DEFAULT_MODEL = "your_default_model_name"
MAX_TOKENS = {
    "outline": 8000,
    "full_script": 8000,
    "dialogue": 8000
}
HOST_PROFILES = """
Host1 (Rachel): Enthusiastic, prone to personal anecdotes.
Host2 (Mike): More analytical, enjoys making pop culture references.
"""
OUTLINE_PROMPT_TEMPLATE = "Your outline prompt template here"
EXPAND_PROMPT_TEMPLATE = "Your expand prompt template here"
DIALOGUE_PROMPT_TEMPLATE = "Your dialogue prompt template here"
```

Adjust these values according to your needs.

## Voice Configuration

PodCastGen uses Microsoft Edge TTS voices. By default:
- Male voice: zh-CN-YunxiNeural
- Female voice: zh-CN-XiaoxiaoNeural

You can list available voices using the `--list-voices` command or check specific language voices with `--list-language`.

