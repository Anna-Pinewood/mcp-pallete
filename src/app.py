from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

from consts import IMAGGA_API_KEY, IMAGGA_API_SECRET

from generate_pallete import generate_palette_image

# Initialize FastMCP server
mcp = FastMCP("weather")


async def get_img_palette(image_path: str) -> dict[str, Any]:
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
    data = await get_img_palette(image_path)
    return json.dumps(data, indent=4)


@mcp.tool()
async def generate_palette_img_tool(image_path: str,
                                    output_path: str,
                                    color_key: str = 'image_colors',
                                    max_colors: int = 7,
                                    width: int = 500,
                                    height: int = 100) -> str:
    data = await get_img_palette(image_path)
    save_path = generate_palette_image(data,
                                       output_path, color_key, max_colors, width, height)
    return f"Palette image generated successfully. Check \"{save_path}\""

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
