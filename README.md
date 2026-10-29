# test01 — Bloxd Texture Realism

A small Windows-friendly Python GUI for sending a local game texture to a hosted image-to-image model and saving the result locally.

## Current implementation

- Model: `black-forest-labs/FLUX.2-klein-9B`
- Provider: `fal-ai`, routed through Hugging Face Inference Providers
- Input formats: PNG, JPG/JPEG, WEBP, BMP
- Input processing: converts to RGB and downscales to a maximum 512 px longest side without changing aspect ratio
- Output: PNG saved into `generated/` next to the source image; the output is resized to the original image dimensions
- Transparency: if the original has non-opaque alpha, the original alpha mask is reapplied to the generated RGB image. The model does not generate new transparency.
- Safety: the original file is not overwritten; existing output names are preserved by adding a numeric suffix

The Hugging Face image-to-image documentation currently gives an explicit `fal-ai` mapping for `black-forest-labs/FLUX.2-klein-9B`. This is a better fit than the previous `timbrooks/instruct-pix2pix` configuration, whose model page did not list an active Inference Provider deployment when checked. See the official docs:

- Image-to-image task and model/provider example: https://huggingface.co/docs/inference-providers/tasks/image-to-image
- InferenceClient authentication and provider routing: https://huggingface.co/docs/huggingface_hub/guides/inference
- Model page: https://huggingface.co/black-forest-labs/FLUX.2-klein-9B

**Important:** documentation listing a model/provider is not a guarantee that your account has free access or that the provider will remain available. Hosted inference may incur charges. Check the current pricing, your account balance/credits, and provider access before running it. This code does not promise free usage.

## Requirements

- Windows 10/11
- Python 3.10 or newer
- A Hugging Face account and a User Access Token with the **Inference Providers** permission
- Access to the configured provider and any required billing/credits

## Install and run (PowerShell)

Clone/download this repository, open PowerShell in the project folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

If PowerShell blocks activation, you can avoid changing execution policy and invoke the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Set the token for the current PowerShell window only, then run the app:

```powershell
$env:HF_TOKEN = "hf_your_token_here"
py main.py
```

Replace the example value with your own token. Do not paste a real token into source code, README, screenshots, or GitHub commits. Do not share it with anyone. The program reads it from the environment variable and does not write it to disk.

To clear it from the current PowerShell session afterward:

```powershell
Remove-Item Env:HF_TOKEN
```

## Privacy and costs

The selected image is sent to Hugging Face and the configured inference provider for processing. Do not use private or sensitive images. The token is sent for authentication to the service and must never be committed to this repository. Provider usage may be billable; verify current pricing and account settings before use. The program makes one image-to-image request per run and does not automatically retry failed requests.

## Texture-specific limitations

- This program is an image-editing prototype, not a dedicated Bloxd.io texture-pack builder.
- It does **not** guarantee seamless tiling, correct game material semantics, or compliance with any particular Bloxd import workflow.
- AI may change small patterns, edge details, or color values. Always inspect the result in an image editor and in-game before replacing any original texture.
- Transparency is restored from the original alpha mask; transparent-region RGB may still be altered by the model, and the mask is not intelligently regenerated.
- The image is resized back to the source dimensions after generation. This preserves the canvas dimensions, not exact original details.
- A maximum 512 px input side is used to reduce transfer size. Output detail and dimensions depend on the hosted model/provider.

## Troubleshooting

- **Missing token:** set `$env:HF_TOKEN` in the same PowerShell window used to launch the app.
- **401/403:** check that the token is valid and has Inference Providers permission; also check account/provider access.
- **402 or quota/billing error:** check current provider pricing, credits, and billing requirements. Do not assume the service is free.
- **Model/provider/task error:** check the current official image-to-image documentation and model page; providers and mappings can change.
- **Timeout/network error:** retry later only after checking whether the previous request was charged; this program does not auto-retry.
- **Tkinter window does not open:** install/use the standard Windows Python distribution that includes Tcl/Tk, then run `py main.py` from a normal desktop session.

## Verification status

The code and configuration were updated against the Hugging Face documentation linked above. The repository edit itself does not prove that a live inference request succeeds from your account: no real token was used and no paid provider request was made as part of this update. Please verify current costs and access before your first run.
