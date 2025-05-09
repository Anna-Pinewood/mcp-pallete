import asyncio
import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP
import json

# from consts import IMAGGA_API_KEY, IMAGGA_API_SECRET

from generate_pallete import generate_palette_image

# Initialize FastMCP server
mcp = FastMCP("mcp-pallete")

IMAGGA_API_KEY = os.getenv("IMAGGA_API_KEY")
IMAGGA_API_SECRET = os.getenv("IMAGGA_API_SECRET")


async def get_img_palette(image_path: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                'https://api.imagga.com/v2/colors',
                auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET),
                files={'image': open(image_path, 'rb')}
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}


# def format_pallete(data: dict[str, Any]) -> str:
#     """
#     Format the palette data from Imagga API into a readable string summary.
#     """
#     try:
#         colors_data = data.get("result", {}).get("colors", {})
#         if not colors_data:
#             return "No color data found in the response."

#         summary = ["Image Color Palette Summary:"]

#         bg_colors = colors_data.get("background_colors", [])
#         if bg_colors:
#             summary.append("\nBackground Colors:")
#             for color in bg_colors[:3]:  # Show top 3
#                 name = color.get("closest_palette_color", "N/A")
#                 html = color.get("html_code", "N/A")
#                 percent = color.get("percent", 0)
#                 summary.append(f"- {name} ({html}), Percent: {percent:.2f}%")

#         fg_colors = colors_data.get("foreground_colors", [])
#         if fg_colors:
#             summary.append("\nForeground Colors:")
#             for color in fg_colors[:3]:  # Show top 3
#                 name = color.get("closest_palette_color", "N/A")
#                 html = color.get("html_code", "N/A")
#                 percent = color.get("percent", 0)
#                 summary.append(f"- {name} ({html}), Percent: {percent:.2f}%")

#         img_colors = colors_data.get("image_colors", [])
#         if img_colors:
#             summary.append("\nImage Colors:")
#             for color in img_colors[:3]:  # Show top 3
#                 name = color.get("closest_palette_color", "N/A")
#                 html = color.get("html_code", "N/A")
#                 percent = color.get("percent", 0)
#                 summary.append(f"- {name} ({html}), Percent: {percent:.2f}%")

#         object_percent = colors_data.get("object_percentage")
#         if object_percent is not None:
#             summary.append(f"\nObject Percentage: {object_percent:.2f}%")

#         return "\n".join(summary)

#     except Exception as e:
#         # Consider logging the error properly in a real application
#         return f"Error formatting palette data: {e}"


@mcp.tool()
async def get_img_palette_tool(image_path: str) -> str:
    """Get the raw color palette data from an image using the Imagga API.

    Args:
        image_path: The local path to the image file.
    """
    data = await get_img_palette(image_path)
    return json.dumps(data, indent=4)


@mcp.tool()
async def generate_palette_img_tool(image_path: str,
                                    output_path: str,
                                    color_key: str = 'image_colors',
                                    max_colors: int = 7,
                                    width: int = 500,
                                    height: int = 100) -> str:
    """Generate a color palette image from an input image.

    Calls the Imagga API to extract colors, then generates an image visualizing
    the dominant colors as vertical stripes.

    Args:
        image_path: The local path to the input image file.
        output_path: The path where the generated palette image will be saved.
        color_key: The key in the Imagga response to use for colors ('image_colors', 'background_colors', 'foreground_colors'). Defaults to 'image_colors'.
        max_colors: The maximum number of dominant colors to include in the palette image. Defaults to 7.
        width: The width of the generated palette image in pixels. Defaults to 500.
        height: The height of the generated palette image in pixels. Defaults to 100.
    """
    data = await get_img_palette(image_path)
    # Check if Imagga call returned an error before proceeding
    if "error" in data or not data.get("result", {}).get("colors"):
         error_message = data.get("status", {}).get("text", "Unknown error fetching colors")
         return f"Error fetching colors from Imagga: {error_message}. Cannot generate palette."
    elif "status" in data and data["status"].get("type") != "success":
         return f"Imagga API call failed: {data['status'].get('text', 'Unknown reason')}"

    try:
        # Run the synchronous function in the default executor
        loop = asyncio.get_running_loop()
        save_path = await loop.run_in_executor(
            None, # Use default executor (ThreadPoolExecutor)
            generate_palette_image, # The function to run
            data,          # Arguments for the function
            output_path,
            color_key,
            max_colors,
            width,
            height
        )
        if save_path: # Check if generate_palette_image returned a path
             return f"Palette image generated successfully. Check \"{save_path}\""
        else:
             # Handle cases where generate_palette_image might return None on error
             return "Failed to generate palette image. Check server logs for details."
    except Exception as e:
        # Log the error properly in a real app
        print(f"Error during palette generation: {e}") # Log to server console
        return f"An error occurred during palette generation: {e}"

if __name__ == "__main__":
    # Initialize and run the server
    print("Starting FastMCP server...")
    mcp.run(transport='stdio')
