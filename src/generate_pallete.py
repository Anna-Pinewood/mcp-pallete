import json
from PIL import Image, ImageDraw
import os
from datetime import datetime
from pathlib import Path
path_project = Path(__file__).parent.parent
path_imgs = path_project / "imgs"
path_outputs = path_imgs / "outputs"


def generate_palette_image(
    color_data: dict,
    output_path: str | None = None,  # Allow None for default path
    color_key: str = 'image_colors',
    max_colors: int = 7,
    width: int = 500,
    height: int = 100
):
    """
    Generates an image with vertical color stripes based on color data.

    Args:
        color_data: Dictionary containing color information, expected to follow
                    the structure of color_response.json.
        output_path: Path to save the generated palette image. If None, uses a
                     default path 'imgs/outputs/img_{color_key}_{timestamp}.png'.
        color_key: Key within color_data['result']['colors'] to use for colors
                   ('background_colors', 'foreground_colors', 'image_colors').
        max_colors: Maximum number of color stripes to include in the palette.
        width: Width of the output image in pixels.
        height: Height of the output image in pixels.
    """
    try:
        colors = color_data.get('result', {}).get('colors', {}).get(color_key, [])
        if not colors:
            print(f"Warning: No colors found for key '{color_key}'. Cannot generate palette.")
            return

        # Sort colors by percentage (descending) and take the top max_colors
        sorted_colors = sorted(colors, key=lambda c: c.get('percent', 0), reverse=True)
        selected_colors = sorted_colors[:max_colors]

        num_colors = len(selected_colors)
        if num_colors == 0:
            print(f"Warning: No colors selected after filtering for key '{color_key}'. Cannot generate palette.")
            return

        # Create a new image
        image = Image.new("RGB", (width, height))
        draw = ImageDraw.Draw(image)

        # Calculate width of each stripe
        stripe_width = width // num_colors
        extra_pixels = width % num_colors  # Distribute remaining pixels

        x_offset = 0
        for i, color_info in enumerate(selected_colors):
            html_code = color_info.get('html_code')
            if not html_code:
                print(f"Warning: Skipping color due to missing 'html_code': {color_info}")
                continue

            current_stripe_width = stripe_width + (1 if i < extra_pixels else 0)

            # Draw the rectangle for the color stripe
            draw.rectangle(
                [(x_offset, 0), (x_offset + current_stripe_width, height)],
                fill=html_code
            )
            x_offset += current_stripe_width

        # Ensure the last stripe covers the full width if rounding caused issues
        if x_offset < width:
            draw.rectangle(
                [(x_offset, 0), (width, height)],
                fill=selected_colors[-1].get('html_code', '#000000')  # Use last valid color or black
            )

        # Determine output path
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"img_{color_key}_{timestamp}.png"
            output_path = path_outputs / filename


        # Save the image
        image.save(output_path)
        print(f"Palette image saved to: {output_path}")
        return output_path
    except KeyError as e:
        print(f"Error: Missing expected key in color data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Example Usage
    json_file_path = os.path.join(os.path.dirname(__file__), 'examples', 'color_response.json')
    # output_image_path = "palette.png" # No longer needed for default path

    try:
        with open(json_file_path, 'r') as f:
            color_data_example = json.load(f)

        # Generate palette using default 'image_colors' and default path
        print("Generating palette from 'image_colors' (default path)...")
        generate_palette_image(
            color_data_example,
            # output_path omitted to use default
            color_key='image_colors',
            max_colors=5
        )

        # Generate palette using 'background_colors' and default path
        # output_bg_path = "palette_background.png" # No longer needed
        print("Generating palette from 'background_colors' (default path)...")
        generate_palette_image(
            color_data_example,
            # output_path omitted
            color_key='background_colors',
            max_colors=3
        )

        # Generate palette using 'foreground_colors' and default path, with custom dimensions
        # output_fg_path = "palette_foreground.png" # No longer needed
        print("Generating palette from 'foreground_colors' (default path, custom size)...")
        generate_palette_image(
            color_data_example,
            # output_path omitted
            color_key='foreground_colors',
            max_colors=3,
            width=300,
            height=50
        )

    except FileNotFoundError:
        print(f"Error: Example JSON file not found at {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {json_file_path}")
