from __future__ import annotations

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image
from huggingface_hub import InferenceClient

# Current Hugging Face image-to-image docs map this model to fal-ai.
# Hosted inference may be billed; check your account's pricing/credits first.
MODEL_ID = "black-forest-labs/FLUX.2-klein-9B"
PROVIDER = "fal-ai"
MAX_SIDE = 512
OUTPUT_DIR_NAME = "generated"
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def choose_image() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    try:
        selected = filedialog.askopenfilename(
            title="選擇一張 Bloxd.io 貼圖",
            filetypes=[
                ("支援的圖片", "*.png *.jpg *.jpeg *.webp *.bmp"),
                ("所有檔案", "*.*"),
            ],
        )
    finally:
        root.destroy()
    return Path(selected) if selected else None


def prepare_image(image: Image.Image, max_side: int = MAX_SIDE) -> Image.Image:
    """Downscale only and return RGB; preserve aspect ratio."""
    image = image.convert("RGB")
    image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return image


def output_path_for(source: Path) -> Path:
    output_dir = source.parent / OUTPUT_DIR_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    candidate = output_dir / f"{source.stem}_realistic.png"
    counter = 2
    while candidate.exists():
        candidate = output_dir / f"{source.stem}_realistic_{counter}.png"
        counter += 1
    return candidate


def main() -> None:
    token = os.getenv("HF_TOKEN")
    if not token:
        messagebox.showerror(
            "缺少 Hugging Face Token",
            "尚未設定 HF_TOKEN。\n\n"
            "此版本使用 Hugging Face Inference Providers 路由至 fal-ai，"
            "需要具有 Inference Providers 呼叫權限的 HF Token。\n"
            "服務可能收費；請先確認帳戶價格/額度。\n"
            "不要把 Token 寫進程式或提交到 GitHub。",
        )
        return

    source = choose_image()
    if source is None:
        print("已取消選取。")
        return
    if source.suffix.lower() not in SUPPORTED_EXTENSIONS:
        messagebox.showerror("不支援的格式", "請選擇 PNG、JPG、JPEG、WEBP 或 BMP 圖片。")
        return

    prompt = (
        "Edit the provided game texture into a more realistic material texture. "
        "Preserve the source image's layout, silhouette, dominant colors, and recognizable pattern. "
        "Add restrained, fine surface detail appropriate to the existing material, not a new scene. "
        "Keep the camera perfectly front-facing and the lighting even and neutral. "
        "No perspective, no objects added, no cast shadow outside the texture, no text, no border. "
        "Keep the overall composition close to the input. This is a flat game texture, not a photograph of a scene."
    )

    try:
        with Image.open(source) as opened:
            original_rgba = opened.convert("RGBA")
            original_size = original_rgba.size
            alpha = original_rgba.getchannel("A")
            # AI image endpoints typically operate on RGB. Transparency is restored as a mask afterward.
            input_image = prepare_image(original_rgba)

        print(f"來源：{source}")
        print(f"原始尺寸：{original_size[0]}x{original_size[1]}")
        print(f"送出尺寸：{input_image.width}x{input_image.height}")
        print(f"模型：{MODEL_ID}（provider：{PROVIDER}）")
        print("圖片將送至遠端推論服務；請勿處理私人或敏感圖片。")
        print("正在呼叫 API……")

        client = InferenceClient(
            provider=PROVIDER,
            api_key=token,
            timeout=240,
        )
        result = client.image_to_image(
            input_image,
            prompt=prompt,
            model=MODEL_ID,
        ).convert("RGB")

        # Keep the original texture dimensions and restore its alpha mask.
        if result.size != original_size:
            result = result.resize(original_size, Image.Resampling.LANCZOS)
        if alpha.getextrema() != (255, 255):
            result.putalpha(alpha)
        else:
            result = result.convert("RGB")

        destination = output_path_for(source)
        result.save(destination, format="PNG")

        print(f"完成：{destination}")
        print(f"輸出尺寸：{result.width}x{result.height}")
        messagebox.showinfo(
            "生成完成",
            f"已儲存圖片：\n{destination}\n\n"
            "輸出尺寸已調整回原圖尺寸；若原圖有透明區域，會沿用原圖 Alpha 遮罩。\n"
            "模型仍可能改變圖案細節，且不保證四邊無縫平鋪，請先檢查結果。",
        )

    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        print(f"生成失敗：{detail}")
        messagebox.showerror(
            "生成失敗",
            f"{detail}\n\n"
            "請依序確認：\n"
            "1. HF_TOKEN 是否有效，且具有 Inference Providers 權限。\n"
            "2. Hugging Face 帳戶是否可使用所選 provider，並有可用額度/付款設定。\n"
            "3. 模型/provider 是否仍支援 image-to-image。\n"
            "4. 網路是否正常。\n\n"
            "本程式不會自動改用其他模型，也不會在失敗時重複送出請求。",
        )


if __name__ == "__main__":
    main()
