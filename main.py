from __future__ import annotations

import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image
from huggingface_hub import InferenceClient

# Open image-to-image model. Availability on hosted inference can change.
MODEL_ID = "timbrooks/instruct-pix2pix"
MAX_SIDE = 512
OUTPUT_DIR_NAME = "generated"


def choose_image() -> Path | None:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askopenfilename(
        title="選擇一張 Bloxd.io 貼圖",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")],
    )
    root.destroy()
    return Path(selected) if selected else None


def resize_for_api(image: Image.Image, max_side: int = MAX_SIDE) -> Image.Image:
    """Downscale only; keep aspect ratio and avoid increasing image dimensions."""
    image = image.convert("RGB")
    image.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
    return image


def main() -> None:
    token = os.getenv("HF_TOKEN")
    if not token:
        messagebox.showerror(
            "缺少 Hugging Face Token",
            "請先設定環境變數 HF_TOKEN，再重新執行。\n"
            "不要把 Token 寫進程式或上傳到 GitHub。",
        )
        return

    source = choose_image()
    if source is None:
        print("已取消選取。")
        return

    prompt = (
        "Transform this game texture into a more photorealistic material texture. "
        "Preserve the original composition, dominant colors, silhouette, and recognizable pattern. "
        "Add subtle realistic surface microdetail appropriate to the existing material. "
        "Flat front-facing texture, even neutral lighting, no perspective, no objects, "
        "no shadows cast outside the texture, no text, suitable for a game texture."
    )

    try:
        with Image.open(source) as original:
            input_image = resize_for_api(original)
            original_size = original.size

        print(f"來源：{source}")
        print(f"原始尺寸：{original_size[0]}x{original_size[1]}")
        print(f"送出尺寸：{input_image.width}x{input_image.height}")
        print(f"模型：{MODEL_ID}")
        print("正在呼叫遠端推論 API；首次執行可能需要等待模型載入……")

        client = InferenceClient(model=MODEL_ID, token=token, timeout=180)
        result = client.image_to_image(input_image, prompt=prompt)

        output_dir = source.parent / OUTPUT_DIR_NAME
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{source.stem}_realistic.png"
        result.save(output_path, format="PNG")

        print(f"完成：{output_path}")
        print(f"輸出尺寸：{result.width}x{result.height}")
        messagebox.showinfo(
            "生成完成",
            f"已儲存圖片：\n{output_path}\n\n"
            "請檢查結果是否保留原貼圖結構及四邊接縫。",
        )

    except Exception as exc:
        print(f"生成失敗：{type(exc).__name__}: {exc}")
        messagebox.showerror(
            "生成失敗",
            f"{type(exc).__name__}: {exc}\n\n"
            "常見原因：Token 無效、模型未提供託管推論、"
            "服務端不支援此任務，或免費額度不足。"
            "\n可在 README 查看替代方案。",
        )


if __name__ == "__main__":
    main()
