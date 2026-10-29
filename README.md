# test01 — Texture Realism API Test

A small local Python prototype for selecting one game texture, sending it to a hosted image-to-image inference API, and saving the result locally. The image is downscaled to at most 512 px on its longest side before upload to reduce bandwidth and inference cost.

## What it does

1. Opens a file picker for a local image.
2. Reads the image and downscales it (never upscales) to at most 512 × 512 while preserving aspect ratio.
3. Calls Hugging Face hosted inference using the `timbrooks/instruct-pix2pix` image-to-image model.
4. Saves the generated PNG to a `generated/` folder next to the source image.

## Requirements

- Python 3.10+
- A Hugging Face account and access token
- Hosted inference availability for the selected model (availability and billing/free quotas can change)

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Set the token securely

Create a token in your Hugging Face account settings. Do **not** commit it to this repository.

**Windows PowerShell (current terminal only):**

```powershell
$env:HF_TOKEN = "hf_your_token_here"
python main.py
```

**Windows Command Prompt (current terminal only):**

```bat
set HF_TOKEN=hf_your_token_here
python main.py
```

Then select a PNG/JPG/WEBP texture in the file picker.

## Important limitations

- This is an API prototype; it has not been validated against every hosted model/provider configuration.
- Hosted inference availability for a specific model can change. If the model is unavailable, choose a currently supported image-to-image model and update `MODEL_ID` in `main.py`.
- A model may alter the original texture rather than preserve it exactly. Review the result before using it.
- This prototype does not yet guarantee seamless tiling, preserve alpha transparency, or integrate with Bloxd.io's texture-pack format.
- A 512 px maximum input side reduces data transfer and resource use, but the remote provider still controls compute limits and may charge for inference.

## Privacy

The selected image is sent to the configured hosted inference provider. Do not upload private or sensitive images. This tool does not upload your Hugging Face token to GitHub; it reads it from the `HF_TOKEN` environment variable.
